1.    Clone repository and open command prompt
2.    Using "cd" command go to project folder
3.    Install/Update all dependencies using command "pip install -r requirements.txt"
4.    Create virtual Python environment: 
      1) python3 -m venv ./Name_of_your_virtual_environment
      2) Name_of_your_virtual_environment\Scripts\activate
5.    Launch Waitress server: "waitress-serve --port=8080 main:app"; 
      If server was launched successfully, then you will see message "INFO:waitress:Serving on http://0.0.0.0:8080"
6.    Open browser and go to http://localhost:8080/api/v1/hello-world-29