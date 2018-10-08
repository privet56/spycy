python autoCoder.py --mode=test --prefix=java --epochs=33 --datadir=data --source=d:/svn/ --max_file_count=1999
rem # 10 hours = 2 epochs
rem python autoCoder.py --mode=train_and_test --prefix=java --epochs=5 --datadir=data --source=d:/svn/ --max_file_count=9999
rem # 2.5 days = 5 epochs
rem python autoCoder.py --mode=train_and_test --prefix=java --epochs=40 --datadir=data --source=d:/svn/ --max_file_count=19999
pause
rem python, fast:
rem python autoCoder.py --mode=test --prefix=py --epochs=2 --datadir=data --source=../ --max_file_count=99
rem java, some hours
rem python autoCoder.py --mode=train_and_test --prefix=java --epochs=6 --datadir=data --source=d:/svn/ --max_file_count=199
rem TODO:
rem python autoCoder.py --mode=train_and_test --prefix=py --epochs=6 --datadir=data --source=d:/svn/ --max_file_count=199
