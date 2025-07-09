## This is for allowing the parking system to print locally.

1. Clone the repo

        git clone https://github.com/pop-o/print.git

2. Create virtual environment

        python -m venv venv

3. Activate virtual environment

        venv\Scripts\activate

4. Install the requirements.

        pip install -r requirements.txt

5. Run the server
        
        cd print
        python manage.py runserver 0.0.0.0:8000
