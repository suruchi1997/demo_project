from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
import os
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def gitcommands(request):
    curr_dir=os.path.dirname(os.path.abspath(__file__))
    root_dir=os.path.abspath(os.path.join(curr_dir, "../.."))
    root_dir=root_dir+"/transata"
    #mkdir
    directories = [
    root_dir+'/ckpt/pretrained_ckpt/imagebind_ckpt/huge',
    root_dir+'/ckpt/pretrained_ckpt/7b_tiva_v0',
    root_dir+'/ckpt/pretrained_ckpt/vicuna_ckpt/7b_v0']
    for directory in directories:
        try:
            subprocess.run(["mkdir","-p",directory],check=True)
        except Exception as e:
            print(e)


    #downloading image bind checkpoint
    url = "https://dl.fbaipublicfiles.com/imagebind/imagebind_huge.pth"
    destination_directory = root_dir+"/ckpt/pretrained_ckpt/imagebind_ckpt/huge"
    command=["wget", "-P",  destination_directory,url]
    try:
        subprocess.run(command)
    except Exception as e:
        print(e)

    #downloading huggingface checkpoints
    command1=[ "huggingface-cli",
            "download",
            "lmsys/vicuna-7b-v1.5",
            "--local-dir",
            root_dir+"/ckpt/pretrained_ckpt/vicuna_ckpt/7b_v0"]


    command2=[
        'huggingface-cli',
        'download',
        '3it/TransVerse-v1',
        '--local-dir',
        root_dir+'/ckpt/pretrained_ckpt/7b_tiva_v0'
    ]

    try:
        subprocess.run(command1,check=True)
        subprocess.run(command2,check=True)
        # out="executed sucessfully"
    except Exception as e:
        print(e)

    #run scripts for data preparation
    try:
        if not os.path.exists(root_dir+"/data"):
            subprocess.run(["mkdir", root_dir+"/data"], check=True)
        if not os.path.exists(root_dir+"/data/T-X_pair_data"):
            subprocess.run(["mkdir", root_dir+"/data/T-X_pair_data"], check=True)
            subprocess.run(["cd", root_dir+"/data/T-X_pair_data"], check=True)

        #image
        os.chdir(root_dir+"/data/T-X_pair_data")
        subprocess.run(["huggingface-cli", "download", "3it/TransVerse-Image-Zip", "--local-dir", "./", "--repo-type", "dataset"], check=True)
        subprocess.run(["unzip", "cc3m.zip"], check=True)
        subprocess.run(["rm", "-rf", "~/.cache/huggingface/hub/datasets--3it--TransVerse-Image-Zip"], check=True)
        subprocess.run(["rm", "cc3m.zip"], check=True)
        # Video
        # subprocess.run(["huggingface-cli", "download", "3it/TransVerse-Video-Zip", "--local-dir", "./", "--repo-type", "dataset"], check=True)
        # subprocess.run(["unzip", "webvid.zip"], check=True)
        # subprocess.run(["rm", "-rf", "~/.cache/huggingface/hub/datasets--3it--TransVerse-Video-Zip"], check=True)
        # subprocess.run(["rm", "webvid.zip"], check=True)
        #Audio
        # subprocess.run(["huggingface-cli", "download", "3it/TransVerse-Audio-Zip", "--local-dir", "./", "--repo-type", "dataset"] , check=True)
        # subprocess.run(["unzip", "audiocap.zip"], check=True)
        # subprocess.run(["rm", "-rf", "~/.cache/huggingface/hub/datasets--3it--TransVerse-Audio-Zip"], check=True)
        # subprocess.run(["rm", "audiocap.zip"], check=True)

    except Exception as e:
        print(e)

    # running miner
    command=[
            'deepspeed',
            '--include', 'localhost:0',
            '--master_addr', '127.0.0.1',
            '--master_port', '28459',
            root_dir+'/neurons/miner.py',
            '--subtensor.network', 'test',
            '--wallet.name', 'tw',
            '--wallet.hotkey', 'tw-h3',
            '--netuid', '74',
            '--axon.port', '8091',
            '--logging.debug',
            '--logging.trace'
    ]
    try:
        subprocess.run(command,check=True)
    except Exception as e:
        print(e)

    # running validator
    command=[
            'deepspeed',
            '--include', 'localhost:0',
            '--master_addr', '127.0.0.1',
            '--master_port', '28459',
            root_dir+' /neurons/validator.py',
            '--subtensor.network', 'test',
            '--wallet.name', 'tw',
            '--wallet.hotkey', 'tw-h3',
            '--netuid', '74',
            '--axon.port', '8091',
            '--logging.debug',
            '--logging.trace'

    ]

    try:
        subprocess.run(command,check=True)
    except Exception as e:
        print(e)

    return JsonResponse({"output":"complete"})


def home(request):
    curr_dir=os.path.dirname(os.path.abspath(__file__))
    root_dir=os.path.abspath(os.path.join(curr_dir, "../.."))

    try:

        repository_url = 'https://github.com/3itSmartLife/TransVerse.git'

                    # Local path where repository will be cloned
        local_path = root_dir+"/transata"

                    # Clone the repository
        res=subprocess.run(['git', 'clone', repository_url, local_path])
        if res.returncode!=0:
            return JsonResponse({'message': 'Error in cloning the Repository'})
        return JsonResponse({'message': 'Repository cloned successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
