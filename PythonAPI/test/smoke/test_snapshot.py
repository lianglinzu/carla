# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

import carla
import random

from . import SyncSmokeTest


class TestSnapshot(SyncSmokeTest):
    def test_spawn_points(self):
        self.world = self.client.reload_world()
        spawn_points = self.world.get_map().get_spawn_points()[:20]
        vehicles = self.world.get_blueprint_library().filter('vehicle.*')
        batch = [(random.choice(vehicles), t) for t in spawn_points]
        batch = [carla.command.SpawnActor(*args) for args in batch]
        response = self.client.apply_batch_sync(batch)

        self.assertFalse(any(x.error for x in response))
        ids = [x.actor_id for x in response]
        self.assertEqual(len(ids), len(spawn_points))

        self.world.tick()
        snapshot = self.world.wait_for_tick()

        self.assertTrue(snapshot == self.world.get_snapshot())

        actors = self.world.get_actors()
        self.assertTrue(all(snapshot.has_actor(x.id) for x in actors))

        for actor_id, t0 in zip(ids, spawn_points):
            actor_snapshot = snapshot.find(actor_id)
            self.assertIsNotNone(actor_snapshot)
            t1 = actor_snapshot.get_transform()
            self.assertAlmostEqual(t0.location.x, t1.location.x, places=2)
            self.assertAlmostEqual(t0.location.y, t1.location.y, places=2)
            self.assertAlmostEqual(t0.location.z, t1.location.z, places=2)
            self.assertAlmostEqual(t0.rotation.pitch, t1.rotation.pitch, places=2)
            self.assertAlmostEqual(t0.rotation.yaw, t1.rotation.yaw, places=2)
            self.assertAlmostEqual(t0.rotation.roll, t1.rotation.roll, places=2)
