import sys
from subprocess import call

from cytomine.models import Job

from neubiaswg5 import CLASS_OBJSEG
from neubiaswg5.helpers import NeubiasJob, prepare_data, upload_data, upload_metrics


def main(argv):
    # 0. Initialize Cytomine client and job if necessary and parse inputs
    with NeubiasJob.from_cli(argv) as nj:
        nj.job.update(status=Job.RUNNING, progress=0, statusComment="Initialisation...")

        problem_cls = CLASS_OBJSEG
        is_2d = True

        # 1. Create working directories on the machine
        # 2. Download the images
        in_images, gt_images, in_path, gt_path, out_path, tmp_path = prepare_data(problem_cls, nj, is_2d=is_2d, **nj.flags)

        # 3. Call the image analysis workflow using the run script
        nj.job.update(progress=25, statusComment="Launching workflow...")
        command = "python script.py --infld {} --outfld {} --blurad {} --radthr {} --intthr {} --spltnt {}".format(in_path, out_path, nj.parameters.blurad, nj.parameters.radthr, nj.parameters.intthr, nj.parameters.spltnt)
        return_code = call(command, shell=True, cwd="/app")  # waits for the subprocess to return

        if return_code != 0:
            err_desc = "Failed to execute the Python script (return code: {})".format(return_code)
            nj.job.update(progress=50, statusComment=err_desc)
            raise ValueError(err_desc)

        # 4. Upload the annotation and labels to Cytomine
        upload_data(problem_cls, nj, in_images, out_path, **nj.flags, is_2d=is_2d, monitor_params={
            "start": 60, "end": 90, "period": 0.1
        })

        # 5. Compute and upload the metrics
        nj.job.update(progress=90, statusComment="Computing and uploading metrics...")
        upload_metrics(problem_cls, nj, in_images, gt_path, out_path, tmp_path, **nj.flags)

        # 6. End
        nj.job.update(status=Job.TERMINATED, progress=100, statusComment="Finished.")


if __name__ == "__main__":
    main(sys.argv[1:])
