# Local Three.js GameBlocks

These are pinned local source references. Inspect only the block that fits the game, then copy or adapt the useful code. Never browse for GameBlocks during a creation task and never add the whole library as a dependency.

Files that import `three` are implementation patterns, not drop-in modules for the PlayDrop template. Adapt them to the Three instance returned by `sdk.libs.three.load()` and carry over the complete local dependency closure named below.

## Camera foundation

- [BaseCameraRig](gameblocks/modules/camera/BaseCameraRig.js): shared camera pose, world-basis, smoothing, and camera application logic. Dependencies: `ScalarUtils`, `Vector3Utils`, `WorldBasis`.
- [PositionFollowCameraRig](gameblocks/modules/camera/PositionFollowCameraRig.js): fixed-azimuth or side-on position following. Dependencies: `BaseCameraRig`, `Vector3Utils`, `WorldBasis`.
- [PoseFollowCameraRig](gameblocks/modules/camera/PoseFollowCameraRig.js): actor or vehicle pose following with speed-aware offsets. Dependencies: `BaseCameraRig`, `Vector3Utils`, `WorldBasis`.
- [WorldBasis](gameblocks/modules/math/WorldBasis.js): one explicit right, up, and forward coordinate contract.
- [ScalarUtils](gameblocks/modules/math/ScalarUtils.js) and [Vector3Utils](gameblocks/modules/math/Vector3Utils.js): camera and motion helpers.

Camera blocks do not choose good framing by themselves. Configure them for the primary surface, frame the player and immediate objective together, and prove the important play area remains visible after resize.

## Core-game helpers

- [PlateTiltController](gameblocks/modules/actor-motion/PlateTiltController.js): maps normalized input intent to a bounded board tilt for marble games.
- [GridPathPlanner](gameblocks/modules/behavior/GridPathPlanner.js): grid path planning for tower defense and board-like navigation.
- [AgentPathNavigator](gameblocks/modules/behavior/AgentPathNavigator.js): moves an agent along a planned world-space path.
- [WaveSpawnDirector](gameblocks/modules/gameplay/WaveSpawnDirector.js): deterministic timed wave spawning with a supplied random generator.
- [RaceCheckpointLapPlay](gameblocks/modules/gameplay/RaceCheckpointLapPlay.js): ordered checkpoints, laps, timing, and race progression.

## Repeatability and cleanup

- [RandomUtils](gameblocks/modules/math/RandomUtils.js): seeded random state for repeatable runs.
- [TimeUtils](gameblocks/modules/math/TimeUtils.js): system or manual clocks. This is not a fixed-timestep simulation loop.
- [Object3DUtils](gameblocks/modules/world/Object3DUtils.js): removes objects and disposes their geometry and materials. Dispose owned texture maps and render targets separately.

Source provenance is recorded in [SOURCE.json](SOURCE.json), and the original terms are in [LICENSE](LICENSE).
