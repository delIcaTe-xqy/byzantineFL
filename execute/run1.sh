for method in fedavg krum trimmed_mean bulyan pefl eppfl
do
    for frac in 0.1 0.2 #0.3 # 注意bulyan的恶意比例限制为n>4f+3
    do
        for p in target untarget
        do
            python main.py --gpu 0 --method $method --tsboard --c_frac $frac --p $p --quantity_skew

        done
    done
done