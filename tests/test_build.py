import json, pathlib, subprocess, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
 def test_catalog_has_no_personal_fleet(self):
  src=json.loads((ROOT/'catalog'/'ship-roles.json').read_text())
  self.assertNotIn('ships',src)
  self.assertGreater(len(src['rulebook']),100)
  self.assertGreater(len(src['codeRules']),100)
  self.assertNotIn('pledge_id',json.dumps(src))
  self.assertNotIn('pledge_cost',json.dumps(src))
 def test_public_build_starts_empty(self):
  subprocess.run([sys.executable,str(ROOT/'scripts'/'build.py')],cwd=ROOT,check=True,capture_output=True)
  html=(ROOT/'index.html').read_text()
  self.assertIn('let ships=[]',html)
  self.assertIn('"ships":[]',html)
  self.assertIn('This is an unofficial Star Citizen fan site',html)
  self.assertNotIn('pledge_id',html)
  self.assertNotIn('pledge_cost',html)
if __name__=='__main__':unittest.main()
