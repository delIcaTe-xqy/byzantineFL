for method in fedavg krum trimmed_mean bulyan pefl eppfl
do
    for alpha in 0.01 0.1 1.0 10.0 100.0
    do
        for p in target untarget
        do
            python main.py --gpu 0 --method $method --tsboard --c_frac 0.2 --alpha $alpha --p $p --quantity_skew
        done
    done
done