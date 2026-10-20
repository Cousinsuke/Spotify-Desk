"""Dependency-free Phase 5.1 checks of shared player UI and LAN assets."""
from pathlib import Path
import unittest

BASE=Path(__file__).resolve().parents[1]

class DeviceUiRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(BASE/'templates/device.html').read_text('utf-8')
        cls.js=(BASE/'static/device.js').read_text('utf-8')
        cls.css=(BASE/'static/device.css').read_text('utf-8')
        cls.routes=(BASE/'device_bridge.py').read_text('utf-8')

    def test_same_player_styles(self):
        self.assertIn('/static/ui.css?v=5.1',self.html)
        self.assertIn('class="surface"',self.html)
        for css_class in ('class="content"', 'class="art-frame"', 'class="details"', 'class="transport"', 'class="bottom"'):
            self.assertIn(css_class,self.html)

    def test_volume_icon_and_slider_present(self):
        self.assertIn('id="volumeIcon"',self.html)
        self.assertIn('id="volume"',self.html)
        self.assertIn('function setVolumeIcon',self.js)
        self.assertIn("doCommand('volume'",self.js)

    def test_ambient_reuses_album_colours_and_audio_meter(self):
        self.assertIn('function updateAmbientFromCover',self.js)
        self.assertIn('--ambient-rgb',self.js)
        self.assertIn('--meter-strength',self.js)
        self.assertIn("classList.toggle('pc-audio'",self.js)

    def test_controls_keep_optimistic_feedback(self):
        self.assertIn('pendingSkip',self.js)
        self.assertIn('optimisticPlay',self.js)
        self.assertIn('Skipping track',self.js)
        self.assertIn('scheduleConfirmation',self.js)

    def test_lan_allows_only_required_shared_stylesheet(self):
        self.assertIn("'/static/ui.css'",self.routes)
        self.assertIn('if not lan_enabled or request.path not in EXPOSED:',self.routes)
        self.assertNotIn("'/static/ui.js'",self.routes)

    def test_failed_cover_does_not_block_new_attempts(self):
        self.assertIn('function retryArtwork(',self.js)
        self.assertIn("artKey='';",self.js)
        self.assertIn("!next.artwork",self.js)
        self.assertIn('showArtworkFallback()',self.js)
        self.assertIn('signal:controller.signal',self.js)

    def test_pairing_token_key_unchanged(self):
        self.assertIn('desk_device_token_v1',self.js)
        self.assertIn('id="pairOverlay"',self.html)
        self.assertIn('id="disconnect"',self.html)

if __name__=='__main__':unittest.main()
