---
vendor: huggingface
title: Introducing Daggr: Chain apps programmatically, inspect visually
original_title: Introducing Daggr: Chain apps programmatically, inspect visually
url: https://huggingface.co/blog/daggr
date: 2026-02-24
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 2075ee6adaee
---


# Introducing Daggr: Chain apps programmatically, inspect visually

					January 29, 2026

Update on GitHub


107

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/608aabf24955d2bfc3cd99c6/-YxmtpzEmf3NKOTktODRP.jpeg)](https://huggingface.co/ariG23498)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63e24395419922d5a6d7a6cc/bOFr0La0VdpIZ06-ZWJa4.jpeg)](https://huggingface.co/emredeveloper)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)](https://huggingface.co/abidlabs)
- [![](https://huggingface.co/avatars/85bb740aa905416c52d3e70fd433bd24.svg)](https://huggingface.co/Gabriel)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/648a374f00f7a3374ee64b99/YPwSOrronoozwHbJchPn3.jpeg)](https://huggingface.co/cfahlgren1)

merve

merve

yuvraj sharma

ysharma

Abubakar Abid

abidlabs

hysts

hysts

Pedro Cuenca

pcuenq

**TL;DR:** [Daggr](https://github.com/gradio-app/daggr) is a new, open-source Python library for building AI workflows that connect Gradio apps, ML models, and custom functions. It automatically generates a visual canvas where you can inspect intermediate outputs, rerun individual steps, and manage state for complex pipelines, all in a few lines of Python code!

## Table of Contents

- [Background](https://huggingface.co/blog/daggr#background)
- [Getting Started](https://huggingface.co/blog/daggr#getting-started)
- [Sharing Your Workflows](https://huggingface.co/blog/daggr#sharing-your-workflows)
- [End-to-End Example with Different Nodes](https://huggingface.co/blog/daggr#end-to-end-example-with-different-nodes)
- [Next Steps](https://huggingface.co/blog/daggr#next-steps)

## Background

If you've built AI applications that combine multiple models or processing steps, you know the pain: chaining API calls, debugging pipelines, and losing track of intermediate results. When something goes wrong in step 5 of a 10-step workflow, you often have to re-run everything just to see what happened.

Most developers either build fragile scripts that are hard to debug or turn to heavy orchestration platforms designed for production pipelines—not rapid experimentation.

We've been working on Daggr to solve problems we kept running into when building AI demos and workflows:

**Visualize your code flow**: Unlike node-based GUI editors, where you drag and connect nodes visually, Daggr takes a code-first approach. You define workflows in Python, and a visual canvas is generated automatically. This means you get the best of both worlds: version-controllable code and visual inspection of intermediate outputs.

**Inspect and Rerun Any Step**: The visual canvas isn't just for show. You can inspect the output of any node, modify inputs, and rerun individual steps without executing the entire pipeline. This is invaluable when you're debugging a 10-step workflow and only step 7 is misbehaving. You can even provide “backup nodes” – replacing one model or Space with another – to build resilient workflows.

**First-Class Gradio Integration**: Since Daggr is built by the Gradio team, it works seamlessly with Gradio Spaces. Point to any public (or private) Space and you can use it as a node in your workflow. No adapters, no wrappers—just reference the Space name and API endpoint.

**State Persistence**: Daggr automatically saves your workflow state, input values, cached results, canvas position—so you can pick up where you left off. Use "sheets" to maintain multiple workspaces within the same app.

## Getting Started

Install daggr with pip or uv, it just requires Python 3.10 or higher:

```
pip install daggr
uv pip install daggr
```

Here's a simple example that generates an image and removes its background. Check out [this Space’s API reference](https://huggingface.co/spaces/hf-applications/Z-Image-Turbo) from the bottom of the Space to see which inputs it takes and which outputs it yields. In this example, the Space returns both original image and the edited image, so we return only the edited image.

```
import random
import gradio as gr
from daggr import GradioNode, Graph

# Generate an image using a Gradio Space
image_gen = GradioNode(
    "hf-applications/Z-Image-Turbo",
    api_name="/generate_image",
    inputs={
        "prompt": gr.Textbox(
            label="Prompt",
            value="A cheetah sprints across the grassy savanna.",
            lines=3,
        ),
        "height": 1024,
        "width": 1024,
        "seed": random.random,
    },
    outputs={
        "image": gr.Image(label="Generated Image"),
    },
)

# Remove background using another Gradio Space
bg_remover = GradioNode(
    "hf-applications/background-removal",
    api_name="/image",
    inputs={
        "image": image_gen.image,  # Connect to previous node's output
    },
    outputs={
        "original_image": None,  # Hide this output
        "final_image": gr.Image(label="Final Image"),
    },
)

graph = Graph(
    name="Transparent Background Generator", 
    nodes=[image_gen, bg_remover]
)
graph.launch()
```

That's it. Run this script and you get a visual canvas served on port 7860 launched automatically, as well as a shareable live link, showing both nodes connected, with inputs you can modify and outputs you can inspect at each step.

[![App](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/daggr-blog/app1.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/daggr-blog/app1.png)

### Node Types

Daggr supports three types of nodes:

**GradioNode** calls a Gradio Space API endpoint or locally served Gradio app. Passing `run_locally=True`, Daggr automatically clones the Space, creates an isolated virtual environment, and launches the app. If local execution fails, it gracefully falls back to the remote API.

```
node = GradioNode(
    "username/space-name",
    api_name="/predict",
    inputs={"text": gr.Textbox(label="Input")},
    outputs={"result": gr.Textbox(label="Output")},
)

# clone a Space locally and serve
node = GradioNode(
    "hf-applications/background-removal",
    api_name="/image",
    run_locally=True,
    inputs={"image": gr.Image(label="Input")},
    outputs={"final_image": gr.Image(label="Output")},
```

**FnNode** — runs a custom Python function:

```
def process(text: str) -> str:
    return text.upper()

node = FnNode(
    fn=process,
    inputs={"text": gr.Textbox(label="Input")},
    outputs={"result": gr.Textbox(label="Output")},
)
```

**InferenceNode** — calls a model via Hugging Face Inference Providers:

```
node = InferenceNode(
    model="moonshotai/Kimi-K2.5:novita",
    inputs={"prompt": gr.Textbox(label="Prompt")},
    outputs={"response": gr.Textbox(label="Response")},
)
```

### Sharing Your Workflows

Generate a public URL with Gradio's tunneling:

```
graph.launch(share=True)
```

For permanent hosting, deploy on Hugging Face Spaces using the Gradio SDK—just add `daggr` to your `requirements.txt`.

## End-to-End Example with Different Nodes

We will now develop an app that takes in an image and generates a 3D asset. This demo can run on daggr 0.4.3. Here are the steps:

- **Take an image, remove the background:** For this, we will clone the [BiRefNet Space](https://huggingface.co/spaces/merve/background-removal) and run it locally.
- **Downscale the image for efficiency:** We will write a simple function for this with FnNode.
- **Generate an image in 3D asset style for better results:** We will use InferenceNode with [Flux.2-klein-4B model](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) on Inference Providers.
- Pass the output image to a 3D generator: We will send the output image to the Trellis.2 Space hosted on Spaces.

> Spaces that are run locally might take models to CUDA (with to.(“cuda”)) or ZeroGPU within the application file. To disable this behavior to run the model on CPU (useful if you have a device with no NVIDIA GPU) duplicate the Space you want to use and clone it.

The resulting graph looks like below.

[![App](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/daggr-blog/app2.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/daggr-blog/app2.png)

Let’s write the first step, which is the background remover. We will clone and run [this Space](https://huggingface.co/spaces/merve/background-removal) locally. This Space runs on CPU, and takes ~13 seconds to run. You can swap with [this app](https://huggingface.co/spaces/hf-applications/background-removal) if you have an NVIDIA GPU.

```
from daggr import FnNode, GradioNode, InferenceNode, Graph

background_remover = GradioNode(
   "merve/background-removal",
   api_name="/image",
   run_locally=True, 
   inputs={
       "image": gr.Image(),
   },
   outputs={
       "original_image": None,
       "final_image": gr.Image(
           label="Final Image"
       ),
   },
)
```

For the second step, we need to write a helper function to downscale the image and pass it to `FnNode`.

```
from PIL import Image
from daggr.state import get_daggr_files_dir


def downscale_image_to_file(image: Any, scale: float = 0.25) -> str | None:
   pil_img = Image.open(image)
   scale_f = max(0.05, min(1.0, float(scale)))
   w, h = pil_img.size
   new_w = max(1, int(w * scale_f))
   new_h = max(1, int(h * scale_f))
   resized = pil_img.resize((new_w, new_h), resample=Image.LANCZOS)
   out_path = get_daggr_files_dir() / f"{uuid.uuid4()}.png"

   resized.save(out_path)
   return str(out_path)
```

We can now pass in the function to initialize the `FnNode`.

```
downscaler = FnNode(
   downscale_image_to_file,
   name="Downscale image for Inference",
   inputs={
       "image": background_remover.final_image,
       "scale": gr.Slider(
           label="Downscale factor",
           minimum=0.25,
           maximum=0.75,
           step=0.05,
           value=0.25,
       ),
   },
   outputs={
       "image": gr.Image(label="Downscaled Image", type="filepath"),
   },
)
```

We will now write the `InferenceNode` with the Flux model.

```
flux_enhancer = InferenceNode(
   model="black-forest-labs/FLUX.2-klein-4B:fal-ai",
   inputs={
       "image": downscaler.image,
       "prompt": gr.Textbox(
           label="prompt",
           value=("Transform this into a clean 3D asset render"),
           lines=3,
       ),
   },
   outputs={
       "image": gr.Image(label="3D-Ready Enhanced Image"),
   },
)
```

> When deploying apps with InferenceNode to Hugging Face Spaces, use a fine-grained Hugging Face access token with the option "Make calls to Inference Providers" only.

Last node is 3D generation with querying the Trellis.2 Space on Hugging Face.

```
trellis_3d = GradioNode(
   "microsoft/TRELLIS.2",
   api_name="/image_to_3d",
   inputs={
       "image": flux_enhancer.image,
       "ss_guidance_strength": 7.5,   
       "ss_sampling_steps": 12,     
   },
   outputs={
       "glb": gr.HTML(label="3D Asset (GLB preview)"),
   },
)
```

Chaining them together and launching the app is as simple as follows.

```
graph = Graph(
   name="Image to 3D Asset Pipeline",
   nodes=[background_remover, downscaler, flux_enhancer, trellis_3d],
)

if __name__ == "__main__":
   graph.launch()
```

You can find the complete example running in [this Space](https://huggingface.co/spaces/merve/daggr-image-to-3d), to run locally you just need to take app.py, install requirements and login to Hugging Face Hub.

## Next Steps

Daggr is in beta and intentionally lightweight. APIs may change between versions, and while we persist workflow state locally, data loss is possible during updates. If you have feature requests or find bugs, please open an issue [here](https://github.com/gradio-app/daggr/issues). We’re looking forward to your feedback! Share your daggr workflows on socials with Gradio for a chance to be featured. Check out all the featured works [here](https://huggingface.co/collections/ysharma/daggr-hf-spaces).

## Models mentioned in this article 1

## Spaces mentioned in this article 4

## Collections mentioned in this article 1

More Articles from our Blog

gradio

workflows

automatic1111

## Rebuilding AUTOMATIC1111 with Gradio Workflow

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1624431552569-noauth.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)

71

September 10, 2026

gradio

workflows

tutorial

## Wire It, Run It, Deploy It: AI Workflows in Gradio

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1624431552569-noauth.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)

49

August 25, 2026

### Community

ArseniyPerchik

Jan 31


edited Jan 31

What about conditional nodes? I mean the node where the next selected node is determined based on the current node's output.

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)](https://huggingface.co/abidlabs)


abidlabs

Article author

Feb 5

This is a great point. We'd like to support them, but are thinking about the right API because we'd also like programmatic inspection / API usage, which requires some level of determinism. If you have any suggestions, please feel free to open an issue here: [https://github.com/gradio-app/daggr](https://github.com/gradio-app/daggr)

hxgdzyuyi

Feb 5

why not jupyternotebook

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)](https://huggingface.co/abidlabs)


abidlabs

Article author

Feb 5

Do you have any issues running Daggr in a jupyter notebook? It should be supported, but if run into issues, please feel free to open an issue here: [https://github.com/gradio-app/daggr](https://github.com/gradio-app/daggr)

MatthewFrank

Feb 9

The visual inspection capability for chained apps is brilliant! Being able to see the flow programmatically while maintaining visibility is so important for debugging and understanding system behavior. Speaking of visualizing system flows, I've been using InfraSketch ([https://www.infrasketch.net/](https://www.infrasketch.net/)) for documenting our application architectures—it generates diagrams from plain English descriptions and lets you refine through conversation. It's been a great complement to tools like Daggr for communicating the overall system design to the broader team.

Funnelsflex

Feb 21


edited Mar 3

This is a solid approach to pipeline transparency. Working with Funnelsflex deployments, we often see a friction point between rigid UI funnel builders and the flexibility of raw Python scripts. Daggr seems to bridge that gap by keeping the logic in the code where it belongs, while providing the visual state persistence that’s usually missing in standard Gradio chains.

The ability to rerun individual nodes without triggering the entire inference stack is a huge win for debugging complex flexible workflows. I’m curious to see how it handles state management when scaling to high-concurrency environments, but for rapid prototyping and 'inspectable' AI apps, it’s a very clean implementation.
[https://funnelsflex.io/](https://funnelsflex.io/)

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fdaggr) or [log in](https://huggingface.co/login?next=%2Fblog%2Fdaggr) to comment


107

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/608aabf24955d2bfc3cd99c6/-YxmtpzEmf3NKOTktODRP.jpeg)](https://huggingface.co/ariG23498)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63e24395419922d5a6d7a6cc/bOFr0La0VdpIZ06-ZWJa4.jpeg)](https://huggingface.co/emredeveloper)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)](https://huggingface.co/abidlabs)
- [![](https://huggingface.co/avatars/85bb740aa905416c52d3e70fd433bd24.svg)](https://huggingface.co/Gabriel)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/648a374f00f7a3374ee64b99/YPwSOrronoozwHbJchPn3.jpeg)](https://huggingface.co/cfahlgren1)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/CWjxjU3HSVmkWBfugVL10.png)](https://huggingface.co/hvbhanot)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1605114051380-noauth.jpeg)](https://huggingface.co/jeffboudier)
- [![](https://huggingface.co/avatars/3a2f12b6111f135e24b4844fdb1b0748.svg)](https://huggingface.co/maxcorbeau)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6415a939e38b2bdc189f1da7/alb9EC84UTeGpVqqGD6VQ.png)](https://huggingface.co/atasoglu)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/J8onuxUInfk_05Jaou5Lq.png)](https://huggingface.co/johnmoonwalker)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1659922312540-610a70f35a40a8bfebfbf09b.jpeg)](https://huggingface.co/mrdbourke)

## Models mentioned in this article 1

## Spaces mentioned in this article 4

## Collections mentioned in this article 1
