---
vendor: huggingface
title: Build a Robot Pick-and-Place Simulation with SimReady Assets
original_title: Build a Robot Pick-and-Place Simulation with SimReady Assets
url: https://huggingface.co/blog/nvidia/simready-assets-robot-pick-and-place
date: 2026-10-30
lang: en
captured: 2026-11-14
extractor: readability-v1
status: ok
body_sha: 444df2c9a768
---

[ Back to Articles](https://huggingface.co/blog)

# Build a Robot Pick-and-Place Simulation with SimReady Assets

Enterprise + Article

Published November 13, 2026


14

- [![](https://huggingface.co/avatars/9f55e9f6faf6a311cccd0c08d0427db5.svg)](https://huggingface.co/ByteSage404)
- [![](https://huggingface.co/avatars/55b482d76fb0269a3e3a1838049b459f.svg)](https://huggingface.co/pomilee)
- [![](https://huggingface.co/avatars/ec3d8d16e74f37584636ad4822d24f26.svg)](https://huggingface.co/jkosnik)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/oSUZPwq6TTEGqIPc62BVo.png)](https://huggingface.co/AiWinstone)
- [![](https://huggingface.co/avatars/7b54d53f6c5d49197fd5399e19dc7b6b.svg)](https://huggingface.co/pipwnz)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)

[![Dillon Bailey's avatar](https://huggingface.co/avatars/ef260ce572881087d516bcf632928740.svg)](https://huggingface.co/dillonb-nv)

Dillon Bailey

dillonb-nv

[![NVIDIA's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)](https://huggingface.co/nvidia) [nvidia](https://huggingface.co/nvidia)

[![Pomi Lee's avatar](https://huggingface.co/avatars/55b482d76fb0269a3e3a1838049b459f.svg)](https://huggingface.co/pomilee)

Pomi Lee

pomilee

[![NVIDIA's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)](https://huggingface.co/nvidia) [nvidia](https://huggingface.co/nvidia)

[![Rishabh Chadha's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/kaRxLMenXEARG7KGBZJUh.png)](https://huggingface.co/rchadha-nv)

Rishabh Chadha

rchadha-nv

[![NVIDIA's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)](https://huggingface.co/nvidia) [nvidia](https://huggingface.co/nvidia)

[![figure-01-pick-and-place-highlight](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/NlngGWIKZEQ8kuWKZtoyM.gif)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/NlngGWIKZEQ8kuWKZtoyM.gif)

This walkthrough showcases a beverage can pick-and-place task that uses the [UR17G arm](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda), [Robotiq 2F-140 gripper](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda), and [beverage can](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd) to compose a scene in Isaac Sim, check their behavior, and run a pick-and-place example with agent-generated controls.

For robotics workflows, SimReady means an [OpenUSD](https://www.nvidia.com/en-us/glossary/openusd/) asset has been prepared with the properties needed for a defined simulation use case, such as collisions, mass, joints, and joint drives. [SimReady Central](https://huggingface.co/spaces/nvidia/simready-central), an open asset library on Hugging Face, lets you reuse robot and object assets with authored simulation properties and profile-validation evidence. For more about the library and its launch, read the [announcement blog](https://huggingface.co/blog/nvidia/simready-central-assets-robotics-ai-factories).

## What makes a robot asset SimReady?

[SimReady Foundation](https://nvidia.github.io/simready-foundation/) defines what features the OpenUSD asset needs for a simulation use case. Its specifications connect three levels:

- Profile: a group of features for a use case, such as a robot body.
- Features: capabilities needed for the use case, such as joints that can be controlled.
- Requirements: checks on the settings needed for each feature, such as a joint’s drive settings.

For this task, those properties include the arm and gripper’s joints and a beverage can asset collisions and mass. Validation checks these settings against the profile’s requirements. The simulation then tests whether the assembled robot can use them to pick up and move the can.

## What comes with the asset, and what do you add?

The [UR17G](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda), [Robotiq 2F-140](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda), and [beverage can](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd) packages include the models and their simulation settings. You assemble the scene and add task code to define the arm–gripper assembly, work surface, starting positions, and controls for moving the arm and opening and closing the gripper.

[![Figure 2](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/J7YL_C3mUh7MWUNJ_pVtN.png)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/J7YL_C3mUh7MWUNJ_pVtN.png)

*Figure 2. SimReady Central supplies the asset models and simulation settings and the example scene and controls define the pick-and-place task.*

## What should you check before running a pick-and-place task?

A robot can look visually correct while stationary in Isaac Sim but move or interact with objects incorrectly when the simulation runs. Before running pick-and-place, test its joints, movement, and contact behavior. You can ask the agent to perform these tests or do them manually in Isaac Sim.

- **Joint settings:** Review the arm and gripper’s joint limits and drive settings.
- **Movement:** Test a small arm movement and open and close the gripper.
- **Contact:** Confirm that the can rests on the work surface without falling through it.

During pick-and-place, watch whether a beverage can stay in the gripper as the arm moves. Asset structures vary, so use the settings in your loaded scene as your starting point. We will be going through the overall process of downloading the assets and composing the scene in the steps below.

## Build a pick-and-place simulation in Isaac Sim

This example combines the [UR17G](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda) arm, [Robotiq 2F-140](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda) gripper, and [beverage can](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd) in Isaac Sim. The task is to grasp the can, lift it, move it to a target, and release it. You can also leverage [SimReady Central Space](http://nvidia-simready-central.hf.space) search service endpoint to look for OEM curated content.

We will also use a frontier AI model to help create and run the task code in an open Isaac Sim scene. For this example, we use GPT-6 Sol, but another agent and model combination may work if it can load the required skills and execute Python against Isaac Sim (generated code and results can vary). The prompt provides a starting point. Inspect the generated code and check the resulting behavior before adapting the task.

**Required Software:**

- Install [Isaac Sim](https://docs.isaacsim.omniverse.nvidia.com/latest/introduction/quickstart_index.html) 6.2, the version used for this example, and check its system requirements.
- Set up an agent of your choice that can use the Isaac Sim skills. Follow the [Agent Skills documentation](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/development_tools/agent_skills.html) to make the bundled skills available to your agent.
- Install the [Hugging Face CLI](https://huggingface.co/docs/huggingface_hub/guides/cli) only if you choose the command-line asset download option.
- Use the [USD Search endpoint](http://nvidia-simready-central.hf.space).

## Step 1: Download the robot arm, gripper, and beverage can assets

Open [SimReady Central](https://huggingface.co/spaces/nvidia/simready-central) and find the [UR17G](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/simready_usd/ur17g_1300.usda) arm, [Robotiq 2F-140](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/9c6b0cedf0066efd474b3bf473e7eaf7ae7e569f/Robotiq_2F_85/simready_usd/Robotiq_2F_85.usda) gripper, and [beverage can](https://huggingface.co/datasets/nvidia/simready-assets/blob/653d91e182011f357cf1644013cc94ddf194d349/food_beverage_can_n01/simready_usd/sm_food_beverage_can_n01_01.usd) used here. Select Download on each asset, then use Save to folder or the supplied Hugging Face command. Keep all three complete asset folders intact so Isaac Sim can find their supporting files.

Use the asset versions linked in this example and provide your agent with the local USD file paths for the arm, gripper, and beverage can. An example gripper path is shown below; your download location may differ.

```
~/ASSETS/hf/src/simready-assets-c7fa7615/Robotiq_2F_140/simready_usd/Robotiq_2F_140.usda
```

[![figure-05-find-robotiq](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/FSec580RNJKj0DIXx9703.gif)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/FSec580RNJKj0DIXx9703.gif)

*Figure 3. SimReady Central search and interactive previews help identify the Robotiq 2F-140 gripper and beverage can used in this example.*

[![figure-04-download-assets](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/LJpqYrl3l5QkQ2T4JJzYd.gif)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/LJpqYrl3l5QkQ2T4JJzYd.gif)

*Figure 4. The beverage can’s download options include saving the asset package to a folder or using the Hugging Face CLI.*

## What does asset validation tell you?

The [arm validation report](https://huggingface.co/datasets/TeradyneRobotics/UniversalRobots/blob/d5d8eb795a487a5c929909bc337ee4834d62b0da/ur17g_1300/.metadata/ur17g_1300_validation.json) uses the Robot-Body 4.0.0 profile and the [gripper validation report](https://huggingface.co/datasets/Robotiq-Official/simready-assets/blob/c7fa7615a353ebac03990208cbc2aa57426f4c48/Robotiq_2F_140/.metadata/Robotiq_2F_140_validation.json) uses Robot-Gripper 3.0.0. Both record passing [PhysX driven-joint checks](https://nvidia.github.io/simready-foundation/latest/features/FET_022_PHYSX.html), which inspect joint-drive settings.

SimReady profile validation provides a shared baseline for reusing these assets. The pick-and-place run then tests how the arm, gripper, can, and controller work together in the assembled scene.

## Step 2: Assemble the robot and compose the scene for pick and place

With the assets downloaded, use your agent with Isaac Sim skills to help assemble the robot, run validation tools, and create the pick-and-place controls. You can also perform these steps manually using the linked documentation.

Start Isaac Sim from its installation directory with the remote Python server enabled so the agent can interact with the simulation through Python:

```
./isaac-sim.sh --enable isaacsim.code_editor.python_server
```

If you are using an agent, make sure you start it from the Isaac Sim directory so that it can access the skills needed while going through the steps below.

Confirm that all three assets appear without missing-file errors. Ask the agent to inspect the arm and gripper’s joint limits and drive settings, or review them yourself in Isaac Sim. The robot and the gripper contain physics joints which can be tested and validated in the Isaac Sim GUI as well. We will now assemble the arm and the gripper next so that we can control the assembly as a single articulation.

You can follow the [Robot Assembler tutorial](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup/assemble_robots.html) for manual assembly. Here we will ask our agent to complete the assembly and validate it for us:

**Sample prompt used in this example:**

```
Assemble the robot arm <local path to Simready ur17g robot usd>
with the gripper <local path to downloded simready Robotiq_2F_140 gripper usd>
using the Robot Assembly tutorial in Isaac Sim
https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup/assemble_robots.html.

Validate the assembly on completion.
```

The agent ends up using the ‘isaac-sim-remote’ and ‘usd-articulation’ skills packaged with Isaac Sim to complete the assembly and validate the physics of the robot. We now have all the assets needed for running pick and place; the assembled robot and the soda can. We will now proceed with the final portion of the workflow.

[![figure-05-joint-settings](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/NcKj9Cbp2iBlXh65rUf0T.gif)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/NcKj9Cbp2iBlXh65rUf0T.gif)

*Figure 5. Joint settings for the UR17G arm and Robotiq 2F-140 gripper in Isaac Sim.*

With the assembled robot and can in the scene, ask the agent to run the task. Evaluate the simulation behavior using the checks in the next step.

## Step 3: Test the controls and run pick-and-place

Now that the assets include simulation properties and profile validation, we can now test in an assembled scene and controller. The controller coordinates the UR17G arm’s movement with the Robotiq 2F-140 gripper’s opening and closing. Use the behavior checks below to evaluate the agent-generated task. To understand or adapt the controller yourself, see the [Adding a Manipulator Robot tutorial](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/core_api_tutorials/tutorial_core_adding_manipulator.html).

**Sample prompt used in this example:**

```
Run pick and place with the assembled robot and soda can
<path to soda can USD from SimReady library> in Isaac Sim.

Ensure you do a contact based grasp for picking up the can and validate
the accuracy/placement error for the pick and place as well.
```

**Skills used**: ‘isaac-sim-remote’, ‘manipulaiton-ik’ and ‘physics-simulation’

The full task tests whether the gripper holds the can during movement and releases it at the target. Reset the scene, then run the approach, grasp, lift, hold, transfer, and release sequence. Compare your run with the opening video and the success criteria below.

[![figure-06-pick-and-place-landscape](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/TBsKTaclDU8oJvkXYCie8.gif)](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/TBsKTaclDU8oJvkXYCie8.gif)

*Figure 6. The UR17G arm and Robotiq 2F-140 gripper move the beverage can from the yellow pickup marker to the green target in Isaac Sim. Shown at 4× speed.*

If your run differs, note where the sequence fails and ask the agent to inspect the scene and generate controls. Reset the can and robot to the same starting state before retrying so you can compare the results.

**Simulation assumptions:**

- **Fixed setup:** The can starts at a known position, with an anchored robot and clear, flat workspace. No vision was used and collision checks were limited.
- **Simplified can:** Deformation and liquid motion are not modeled, so this example does not test crushing.
- **Scripted grasp and motion:** A horizontal grasp uses a 2 N·m drive-effort cap chosen through simulation tests, not calibrated to fingertip forces or recommended by the manufacturer. Contact and friction hold the beverage can as the arm follows fixed waypoints without replanning. For hardware gripping-force specifications, see the [Robotiq product sheet](https://robotiq.com/hubfs/Product-sheets/Adaptive%20Grippers/Product-sheet-Adaptive-Grippers-EN.pdf).

These results apply to this scripted setup. They do not establish robustness to uncertain object positions, different payloads, or real hardware.

## Build your next simulation with SimReady Assets

Build your own pick-and-place task with assets from [SimReady Central](https://huggingface.co/spaces/nvidia/simready-central), then use an agent of your choice to help assemble the scene and run it in Isaac Sim.

**Discover assets**

- **Find robots and objects:** Browse [SimReady Central](https://huggingface.co/spaces/nvidia/simready-central) on Hugging Face.
- **Check what an asset supports:** Review the profiles and requirements in [SimReady Foundation](https://nvidia.github.io/simready-foundation/latest/) alongside the asset’s validation reports.

**Build a pick-and-place scene**

- **Set up the simulator:** Follow the [Isaac Sim installation guide](https://docs.isaacsim.omniverse.nvidia.com/latest/introduction/quickstart_index.html) for the version used in this example.
- **Connect your agent:** Follow the [Isaac Sim Agent Skills documentation](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/development_tools/agent_skills.html) to make the bundled skills available to your agent.
- **Assemble the robot:** Follow the [Robot Assembler tutorial](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup/assemble_robots.html#assembling-robots) if you prefer to connect the arm and gripper manually.

**Prepare and contribute content**

- **Start from CAD:** Follow the [5 Steps to Create SimReady Assets for Robotics](https://developer.nvidia.com/blog/5-steps-to-create-simready-assets-for-robotics-with-frontier-ai-models/) to prepare your own robotics assets.
- **Validate and submit assets:** Follow the [SimReady Central submission guide](https://github.com/NVIDIA-Omniverse/simready-central/blob/main/.agents/skills/submit-simready-assets/SKILL.md) to make your assets available to other developers.

For inspiration, explore [Michael Wagner’s voice-controlled VR demo](https://lnkd.in/p/g3-5svW6) or [Maziyar Panahi’s Microduck simulation](https://lnkd.in/p/gnxQ3YS8). Both show how developers are using SimReady assets in their own projects.

What will you build? Share your scene and results in the Hugging Face comments, including the assets and Isaac Sim version you used.

Happy building!

## Datasets mentioned in this article 3

## Spaces mentioned in this article 1

More from this author

## *Evaluating Privacy Protection and Practical AI Applications with 100,000 Synthetic Business Documents Across Eight Domains*

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)

5

November 9, 2026

## Nemotron-Personas-Finance-Japan: A Synthetic Dataset Capturing Japan's Demographics and Financial Context

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65df9200dc3292a8983e5017/Vs5FPVCH-VZBipV3qKTuy.png)

19

November 9, 2026

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or clicking here.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fnvidia%2Fsimready-assets-robot-pick-and-place) or [log in](https://huggingface.co/login?next=%2Fblog%2Fnvidia%2Fsimready-assets-robot-pick-and-place) to comment


14

- [![](https://huggingface.co/avatars/9f55e9f6faf6a311cccd0c08d0427db5.svg)](https://huggingface.co/ByteSage404)
- [![](https://huggingface.co/avatars/55b482d76fb0269a3e3a1838049b459f.svg)](https://huggingface.co/pomilee)
- [![](https://huggingface.co/avatars/ec3d8d16e74f37584636ad4822d24f26.svg)](https://huggingface.co/jkosnik)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/oSUZPwq6TTEGqIPc62BVo.png)](https://huggingface.co/AiWinstone)
- [![](https://huggingface.co/avatars/7b54d53f6c5d49197fd5399e19dc7b6b.svg)](https://huggingface.co/pipwnz)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)
- [![](https://huggingface.co/avatars/6b59ac5f151b322f5261adacecce6b61.svg)](https://huggingface.co/yiucw)
- [![](https://huggingface.co/avatars/a045d5a990db610dd1f4abbcca7f1bd6.svg)](https://huggingface.co/klnadim)
- [![](https://huggingface.co/avatars/f42dac7bbb5f8a8dd315bdbe623813e6.svg)](https://huggingface.co/ExceedZhang)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/683acf96542967b165847cff/tUHvC7omJt6mPPdyx1oSe.png)](https://huggingface.co/safikhan5834)
- [![](https://huggingface.co/avatars/604ef02c6a6eac9315df923eaf7e56b4.svg)](https://huggingface.co/Eumoren)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a980914cb03264ff33c4e0c/zOqgwh5M1nCzjQGfrT0Je.jpeg)](https://huggingface.co/willemelliw)

## Datasets mentioned in this article 3

## Spaces mentioned in this article 1
