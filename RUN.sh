source venv/bin/activate
nohup python3 elk_bot_main.py &
nohup python3 elk_daily_report.py &
nohup python3 synchronize_gsh_with_db.py &
