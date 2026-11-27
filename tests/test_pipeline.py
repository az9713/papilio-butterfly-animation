import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from pipeline_common import load_config,validate_config,validate_tag,png_size,configure_device

ROOT=Path(__file__).resolve().parents[1]


class ConfigurationTests(unittest.TestCase):
    def setUp(self):self.config=json.loads((ROOT/'config.json').read_text())

    def test_default_and_explicit_override_precedence(self):
        config,overrides=load_config(ROOT/'config.json')
        self.assertEqual(config,self.config);self.assertEqual(overrides,{})
        config,overrides=load_config(ROOT/'config.json',resolution=[640,360],samples=8)
        self.assertEqual(config['resolution'],[640,360]);self.assertEqual(config['final_samples'],8)
        self.assertEqual(set(overrides),{'resolution','final_samples'})
        self.assertEqual(json.loads((ROOT/'config.json').read_text()),self.config)

    def test_invalid_controls_are_rejected(self):
        cases=[('fps',True),('fps',0),('camera_orbits',1.5),('camera_orbits',-1),
               ('resolution',[641,360]),('resolution',[640]),('final_samples',0),
               ('duration_seconds',0),('duration_seconds',1.01),('wing_period_seconds',5),
               ('light_period_seconds',5),('metal_roughness',1.1),('enamel_roughness',-1),
               ('camera_radius',0),('camera_height',float('nan')),('title',''),('lighting_revision',3)]
        for key,value in cases:
            with self.subTest(key=key,value=value):
                config=copy.deepcopy(self.config);config[key]=value
                with self.assertRaises(ValueError):validate_config(config)

    def test_unknown_and_missing_fields_are_rejected(self):
        config=copy.deepcopy(self.config);config['camera_orbit']=2
        with self.assertRaises(ValueError):validate_config(config)
        config=copy.deepcopy(self.config);del config['camera_orbits']
        with self.assertRaises(ValueError):validate_config(config)

    def test_zero_motion_is_supported(self):
        config=copy.deepcopy(self.config);config.update(camera_orbits=0,wing_amplitude_degrees=0,
                                                       light_breath_fraction=0,wing_period_seconds=5,
                                                       light_period_seconds=5)
        validate_config(config)

    def test_checkpoint_path_injection_is_rejected(self):
        for tag in ['../final-v01','../x','/root','..','a/b','a\\b']:
            with self.subTest(tag=tag),self.assertRaises(ValueError):validate_tag(tag)
        self.assertEqual(validate_tag('final-v02'),'final-v02')

    def test_png_integrity_detects_truncation(self):
        self.assertEqual(png_size(ROOT/'papilio-poster.png'),[1920,1080])
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'broken.png';path.write_bytes((ROOT/'papilio-poster.png').read_bytes()[:100])
            with self.assertRaises(ValueError):png_size(path)

    def test_auto_device_falls_back_to_cpu_without_a_gpu(self):
        prefs=SimpleNamespace(devices=[],compute_device_type=None,get_devices=lambda:None)
        fake=SimpleNamespace(context=SimpleNamespace(preferences=SimpleNamespace(
            addons={'cycles':SimpleNamespace(preferences=prefs)})))
        scene=SimpleNamespace(render=SimpleNamespace(engine='CYCLES'),cycles=SimpleNamespace())
        with patch.dict('sys.modules',{'bpy':fake}):
            self.assertEqual(configure_device(scene,'auto')['selected'],'CPU')
            self.assertEqual(scene.cycles.device,'CPU')
            with self.assertRaises(RuntimeError):configure_device(scene,'optix')


if __name__=='__main__':unittest.main()
