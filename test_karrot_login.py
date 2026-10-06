import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import urlencode
import karrot_login as k

class LoginTests(unittest.TestCase):
    def test_pkce_rfc7636(self):
        self.assertEqual(k.challenge('dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk'), 'E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM')

    def test_callback(self):
        path='/callback?' + urlencode({'code':'test-code','state':'expected','iss':k.ISSUER})
        self.assertEqual(k.parse_callback(path,'expected'),'test-code')
        with self.assertRaises(ValueError): k.parse_callback(path,'different')
        with self.assertRaises(ValueError): k.parse_callback('/callback?state=expected&code=x','expected')
        with self.assertRaises(ValueError): k.parse_callback(path+'&state=another','expected')

    def test_save(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'auth.json'
            k.save_tokens({'access_token':'fake','token_type':'Bearer'},dest)
            self.assertEqual(json.loads(dest.read_text())['resource'],k.MCP)
            with self.assertRaises(FileExistsError):
                k.save_tokens({'access_token':'fake','token_type':'Bearer'},dest)

    def test_manifest(self):
        client=json.loads(Path('karrot-client.json').read_text())
        self.assertEqual(client['client_id'],k.CLIENT_ID)
        self.assertEqual(client['redirect_uris'],[k.REDIRECT])

if __name__=='__main__': unittest.main()
