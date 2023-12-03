rm -rf ./__pycache__
rm -rf ./sensor/__pycache__
rm -rf ./ui/__pycache__
rm ./nohup.out
echo -e "from SharedMemory import SharedMemory\nnamespace={'FT':'"$RANDOM"','SideCam':{'Adjustment':'"$RANDOM"','data':'"$RANDOM"'},'DVS':'"$RANDOM"','RGB':'"$RANDOM"'}" > ./com.py
nohup python sensor/ft.py &
#nohup python sensor/sideCam.py &
nohup python sensor/dv.py &
nohup python ui/main.py &