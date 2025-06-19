for method in eppfl
do
    python main.py --gpu 0 --method $method --tsboard --c_frac 0.0 --quantity_skew --debug
done