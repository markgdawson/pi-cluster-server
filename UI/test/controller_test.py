import os
import shutil
import glob
import numpy as np
from controller import Controller
import settings
import cluster_manager
from tempfile import mkdtemp

from computedrag import compute_drag_for_simulation 

tmpdir = mkdtemp()+'/'

class TestController(object):

    def setup(self):
        settings.cluster_path = mkdtemp()+'/'
        settings.cluster_address = 'localhost'
        cluster_manager.cluster_path = settings.cluster_path
        cluster_manager.cluster_address = 'localhost'

        if os.path.exists(settings.cluster_path):
            shutil.rmtree(settings.cluster_path)
        os.makedirs(settings.cluster_path+'/inbox')
        os.makedirs(settings.cluster_path+'/signal')
        os.makedirs(settings.cluster_path+'/signal_out')
        os.makedirs(settings.cluster_path+'/outbox')

        if not os.path.exists('signal'):
            os.makedirs('signal')

        self.complete_index = '1234'

        self.complete_runpath = 'outbox/run' + self.complete_index
        if os.path.exists(self.complete_runpath):
            shutil.rmtree(self.complete_runpath)
        os.makedirs(self.complete_runpath)

        for filename in glob.glob('test/data/*'):
            shutil.copy(filename, self.complete_runpath)
        
        self.controller = Controller()

    def teardown(self):
        if os.path.exists(settings.cluster_path):
            shutil.rmtree(settings.cluster_path)

        shutil.rmtree(self.complete_runpath)


    def test_init(self):
        assert self.controller.offset == [0, 0]
        assert self.controller.scale == [1.0, 1.0]
        assert len(self.controller.contour.shape) == 2

        assert isinstance(self.controller.current_name, str)

        assert self.controller.background.shape == (480, 640)

    def test_calibrate(self):
        self.controller.background = None
        self.controller.calibrate()

        assert self.controller.background.shape == (480, 640)

    def test_capture(self):
        frame, depth_rgb = self.controller.capture()

        assert frame.shape == (480, 640, 3)
        assert depth_rgb.shape == (480, 640, 3)

    def test_get_user_details(self):
        frame, depth_rgb = self.controller.capture()

        assert frame.shape == (480, 640, 3)
        assert depth_rgb.shape == (480, 640, 3)

    def test_start_simulation(self):
        # Get the background
        self.controller.calibrate()
        frame, depth_rgb = self.controller.capture()
        self.controller.set_user_details('Tester', 'anemail@dotcom.com')

        index = self.controller.start_simulation()

        assert os.path.exists(settings.cluster_path+'inbox')
        assert os.path.exists(settings.cluster_path+'inbox/run'+str(index))
        assert os.path.exists(settings.cluster_path+'signal/run'+str(index))

        loaded_simulation = cluster_manager.load_simulation(index)

        assert loaded_simulation['name'] == 'Tester'

        shutil.rmtree('outbox/run'+str(index))

    def test_compute_drag(self):
        drag = compute_drag_for_simulation(self.complete_index)
        assert drag == 180.0

    def test_postprocess(self):
        self.controller.simulation_postprocess(self.complete_index)
        assert os.path.exists('drag_cache.npy')
        assert self.controller.drag[-1,1] == '180.0'

    def test_print_simulation(self):
        s=cluster_manager.load_simulation(self.complete_index)
        new_index = self.complete_index+'0'
        for filename in glob.glob(self.complete_runpath+'/*'):
            shutil.copy(filename, self.complete_runpath+'0')
        s['drag'] = 10
        s['index'] = new_index
        cluster_manager.save_simulation(s)
        s=cluster_manager.load_simulation(new_index)
        print(s['drag'])
        self.controller.print_simulation(
            new_index,
            send_to_printer = False
        )
        assert os.path.exists(new_index+'.pdf')
        #os.remove('test_pil.pdf')

    def test_best_simulations(self):
        self.controller.drag = np.array([[self.complete_index, -5]])
        simulations = self.controller.best_simulations()
        assert len(simulations) > 0
        assert simulations['1234']['name'] == 'Tester'

    def test_get_epoch(self):
        time = self.controller.get_epoch()
        assert time > 0

