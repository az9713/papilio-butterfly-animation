"""Shared configuration, render validation, and receipts. Standard library only."""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import uuid
import zlib

ROOT = Path(__file__).resolve().parent
CONFIG_KEYS = {
    'title', 'duration_seconds', 'fps', 'resolution', 'wing_period_seconds',
    'wing_rest_degrees', 'wing_amplitude_degrees', 'lower_wing_amplitude_factor',
    'camera_orbits', 'camera_radius', 'camera_height', 'camera_lens_mm',
    'camera_target_height', 'camera_start_degrees', 'light_period_seconds',
    'light_breath_fraction', 'root_height', 'root_tilt_degrees',
    'metal_roughness', 'enamel_roughness', 'lighting_revision', 'final_samples',
}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def path_label(path):
    path = Path(path).resolve()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return 'external/' + path.name


def write_json(path, value, *, replace=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w' if replace else 'x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def receipt_path(folder, prefix):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    return Path(folder) / (prefix + '-' + stamp + '-' + uuid.uuid4().hex[:8] + '.json')


def receipt(kind, **values):
    return {'schema_version': 1, 'kind': kind,
            'recorded_at_utc': datetime.now(timezone.utc).isoformat(), **values}


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError('Configuration must be a JSON object')
    missing, unknown = CONFIG_KEYS - config.keys(), config.keys() - CONFIG_KEYS
    if missing or unknown:
        raise ValueError(f'Configuration keys: missing={sorted(missing)}, unknown={sorted(unknown)}')
    if not isinstance(config['title'], str) or not config['title'].strip():
        raise ValueError('title must be a nonempty string')
    for key in CONFIG_KEYS - {'title', 'resolution'}:
        value = config[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(key + ' must be a finite number')
    for key in ['fps', 'final_samples', 'lighting_revision', 'camera_orbits']:
        if type(config[key]) is not int:
            raise ValueError(key + ' must be an integer')
    for key in ['duration_seconds', 'wing_period_seconds', 'light_period_seconds',
                'camera_radius', 'camera_lens_mm', 'root_height']:
        if config[key] <= 0:
            raise ValueError(key + ' must be positive')
    if not 1 <= config['fps'] <= 240 or not 1 <= config['final_samples'] <= 65536:
        raise ValueError('fps must be 1..240; final_samples must be 1..65536')
    if config['lighting_revision'] not in [1, 2] or config['camera_orbits'] < 0:
        raise ValueError('lighting_revision must be 1 or 2; camera_orbits must be nonnegative')
    size = config['resolution']
    if not isinstance(size, list) or len(size) != 2 or any(
            type(n) is not int or n < 16 or n > 16384 or n % 2 for n in size):
        raise ValueError('resolution must contain two even integers from 16 to 16384')
    for key in ['metal_roughness', 'enamel_roughness', 'light_breath_fraction']:
        if not 0 <= config[key] <= 1:
            raise ValueError(key + ' must be in [0, 1]')
    for key in ['wing_amplitude_degrees', 'lower_wing_amplitude_factor']:
        if config[key] < 0:
            raise ValueError(key + ' must be nonnegative')
    frames = config['duration_seconds'] * config['fps']
    if not math.isclose(frames, round(frames), abs_tol=1e-7) or frames < 2:
        raise ValueError('duration_seconds * fps must be an integer of at least two frames')
    for key, active in [('wing_period_seconds', config['wing_amplitude_degrees'] != 0),
                        ('light_period_seconds', config['light_breath_fraction'] != 0)]:
        cycles = config['duration_seconds'] / config[key]
        if active and not math.isclose(cycles, round(cycles), abs_tol=1e-7):
            raise ValueError(key + ' must divide duration_seconds for a seamless loop')
    return config


def load_config(path, *, resolution=None, samples=None):
    config = json.loads(Path(path).read_text(encoding='utf-8'))
    validate_config(config)
    overrides = {}
    if resolution is not None:
        overrides['resolution'] = list(resolution)
    if samples is not None:
        overrides['final_samples'] = samples
    config = {**config, **overrides}
    validate_config(config)
    return config, overrides


def validate_tag(tag):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', tag):
        raise ValueError('Checkpoint tag must be a simple name, not a path')
    return tag


def verify_protected_assets(root, baseline):
    root=Path(root)
    packaged=(root/'package-manifest.json').is_file()
    contract=json.loads((root/'development/protected-assets.json').read_text())
    declared={entry['path'] for entry in json.loads((root/'package-manifest.json').read_text())['files']} if packaged else None
    checked=[];omitted=[]
    for name,working_digest in baseline['protected_assets'].items():
        path=root/name
        if not path.is_file():
            if packaged and name not in declared:omitted.append(name);continue
            raise RuntimeError('Protected asset is missing: '+name)
        expected=contract['assets'][name]['canonical_git_sha256'] if packaged else working_digest
        if sha256(path)!=expected:raise RuntimeError('Protected asset changed: '+name)
        checked.append(name)
    return {'mode':'canonical-source-bytes' if packaged else 'working-copy-bytes',
            'checked':len(checked),'intentionally_omitted':omitted}


def configure_device(scene, requested='auto'):
    """An explicit backend must exist; auto prefers OptiX/CUDA/... then CPU."""
    import bpy
    if scene.render.engine != 'CYCLES':
        return {'requested': requested, 'selected': 'engine-managed', 'devices': []}
    prefs = bpy.context.preferences.addons['cycles'].preferences
    requested = requested.lower()
    candidates = ['OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI'] if requested == 'auto' else [requested.upper()]
    for backend in candidates:
        if backend == 'CPU':
            break
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
        except (TypeError, ValueError, RuntimeError):
            continue
        matching = [device for device in prefs.devices if device.type == backend]
        if matching:
            for device in prefs.devices:
                device.use = device.type == backend
            scene.cycles.device = 'GPU'
            scene.cycles.denoiser = 'OPTIX' if backend == 'OPTIX' else 'OPENIMAGEDENOISE'
            return {'requested': requested, 'selected': backend,
                    'devices': [device.name for device in matching]}
    if requested not in ['auto', 'cpu']:
        raise RuntimeError('Requested Cycles backend is unavailable: ' + requested)
    scene.cycles.device = 'CPU'
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    return {'requested': requested, 'selected': 'CPU', 'devices': ['CPU']}


def png_size(path):
    """Validate PNG chunk CRCs and compressed image data without Pillow."""
    data = Path(path).read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Invalid PNG signature: ' + str(path))
    offset, size, end, payload = 8, None, False, bytearray()
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError('Truncated PNG chunk: ' + str(path))
        length = struct.unpack('>I', data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        chunk = data[offset + 8:offset + 8 + length]
        next_offset = offset + length + 12
        if next_offset > len(data) or zlib.crc32(kind + chunk) & 0xffffffff != struct.unpack(
                '>I', data[offset + 8 + length:next_offset])[0]:
            raise ValueError('PNG chunk integrity failure: ' + str(path))
        if kind == b'IHDR':
            size = list(struct.unpack('>II', chunk[:8]))
        if kind == b'IDAT':
            payload.extend(chunk)
        if kind == b'IEND':
            end = True
            if next_offset != len(data):
                raise ValueError('Trailing bytes after PNG end')
        offset = next_offset
    decoder = zlib.decompressobj()
    decoder.decompress(bytes(payload))
    if not size or not end or not payload or not decoder.eof:
        raise ValueError('Incomplete PNG: ' + str(path))
    return size
