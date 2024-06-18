import os
import csv
import random
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key
IMAGES_CSV = 'images.csv'
NUM_SETS = 20

categories = {
    'quality': ['poor', 'fair', 'excellent'],
    'ethnicity': ['asian', 'caucasian', 'black', 'unintelligible'],
    'gender': ['feminine', 'neutral', 'masculine', 'unintelligible']
}

def shuffle_images():
    with open(IMAGES_CSV, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        images = [row['image_url'] for row in reader]
    random.shuffle(images)
    with open('shuffled_images.txt', 'w') as f:
        for image in images:
            f.write(image + '\n')
    return images

def load_shuffled_images():
    if not os.path.exists('shuffled_images.txt'):
        return shuffle_images()
    with open('shuffled_images.txt', 'r') as f:
        images = [line.strip() for line in f]
    return images

def create_sections(images, num_sets):
    set_size = len(images) // num_sets
    sections = [images[i * set_size:(i + 1) * set_size] for i in range(num_sets)]
    for i in range(len(images) % num_sets):
        sections[i].append(images[num_sets * set_size + i])
    with open('sections.txt', 'w') as f:
        for section in sections:
            f.write(','.join(section) + '\n')
    return sections

def load_sections():
    if not os.path.exists('sections.txt'):
        images = load_shuffled_images()
        return create_sections(images, NUM_SETS)
    with open('sections.txt', 'r') as f:
        sections = [line.strip().split(',') for line in f]
    return sections

def get_user_set(user_id):
    sections = load_sections()
    user_assignments = load_user_assignments()
    if user_id in user_assignments:
        return sections[int(user_assignments[user_id])]
    user_index = len(user_assignments) % NUM_SETS
    user_assignments[user_id] = user_index
    save_user_assignments(user_assignments)
    return sections[user_index]

def load_user_assignments():
    if not os.path.exists('user_assignments.txt'):
        return {}
    with open('user_assignments.txt', 'r') as f:
        return dict(line.strip().split(':') for line in f)

def save_user_assignments(assignments):
    with open('user_assignments.txt', 'w') as f:
        for user_id, section in assignments.items():
            f.write(f'{user_id}:{section}\n')

def save_progress(user_id, index):
    progress_file = os.path.join('experiment', 'sample', user_id, 'progress.txt')
    if not os.path.exists(os.path.dirname(progress_file)):
        os.makedirs(os.path.dirname(progress_file))
    with open(progress_file, 'w') as f:
        f.write(str(index))

def load_progress(user_id):
    progress_file = os.path.join('experiment', 'sample', user_id, 'progress.txt')
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return int(f.read())
    return 0

def save_labels(user_id, data):
    user_folder = os.path.join('experiment', 'sample', user_id)
    os.makedirs(user_folder, exist_ok=True)
    csv_file = os.path.join(user_folder, 'image_labels.csv')
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='') as csvfile:
        fieldnames = ['image', 'quality', 'ethnicity', 'gender']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if "intro_shown" not in session:
        session["intro_shown"] = True
        return render_template('intro.html')

    user_id = session['user_id']
    
    if 'images' not in session:
        session['images'] = get_user_set(user_id)
        session['index'] = load_progress(user_id)
    
    images = session['images']
    index = session['index']

    if request.method == 'POST':
        if 'next' in request.form:
            quality = request.form.get('quality')
            ethnicity = request.form.get('ethnicity')
            gender = request.form.get('gender')
            image = images[index]
            save_labels(user_id, {'image': image, 'quality': quality, 'ethnicity': ethnicity, 'gender': gender})
            index += 1
            session['index'] = index
            save_progress(user_id, index)
            if index >= len(images):
                return redirect(url_for('complete'))

    if index < len(images):
        current_image = images[index]
        return render_template('index.html', image=current_image, categories=categories)
    else:
        return redirect(url_for('complete'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user_folder = os.path.join('experiment', 'sample', user_id)
        os.makedirs(user_folder, exist_ok=True)
        session['user_id'] = user_id
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/complete')
def complete():
    return "All images have been categorized!"

if __name__ == '__main__':
    app.run(debug=True)
