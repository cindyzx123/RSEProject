from flask import Flask, render_template, request, redirect, url_for, abort, session
import recognize_video
import lock_module
import json_operations

import argparse

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
	if request.method == "POST":
		if request.form["button"] == "start":
			return redirect(url_for('user'))
	else:
		return render_template('home.html')

@app.route("/camera", methods=["GET", "POST"])
def camera():
    
    if request.method == "POST":
        if request.form["button"] == "back":
            return redirect(url_for('user'))
    else:
        ap = argparse.ArgumentParser()

        ap.add_argument("-rl", "--relearn", required=True,
            help="if there is photo to be relearned")
        args = vars(ap.parse_args())

        need_to_learn = args["relearn"]

        identified_record = recognize_video.process_video(need_to_learn,"face_detection_model",
            "openface_nn4.small2.v1.t7","output/recognizer.pickle","output/le.pickle",0.5)

        # check man at door and if he/she is home owner
        door = "unknown"
        biggest_val = -1
        for key,val in identified_record.items():
            if val > biggest_val:
                door = key
                biggest_val = val

        f = open("homeowners.txt", "r")
        for line in f:
            line = line.rstrip()
            if line == door:
                lock_module.open_lock()
                return render_template('demo.html', name=door, homeowner="True")
            elif line == '':
                return render_template('demo.html', name=door)

        return render_template('demo.html', name=door)

    ap = argparse.ArgumentParser()

    ap.add_argument("-rl", "--relearn", required=True,
		help="if there is photo to be relearned")
    args = vars(ap.parse_args())

    need_to_learn = args["relearn"]

    identified_record = recognize_video.process_video(need_to_learn,"face_detection_model",
        "openface_nn4.small2.v1.t7","output/recognizer.pickle","output/le.pickle",0.5)

    door = json_operations.readFromJSONFile('whos_at_door')

    # check man at door and if he/she is home owner
    return render_template('demo.html', name=list(door.keys())[0])

@app.route("/lock")
def lock():
	state = lock_module.check_lock_status()
	return render_template('lock.html', lock_status = state)

@app.route('/update_lock/<state>', methods=["PUT"])
def update_lock(state):
    if (state == 'open'):
        lock_module.open_lock()
    if (state == 'lock'):
        lock_module.lock_lock()
    return state

if __name__ == '__main__':
    app.run(debug=True, port = 8000)