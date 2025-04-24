with open("hand.txt", 'r') as hand, open("target_to_cam.txt", 'r') as eye, open("hand_to_eye.txt", 'w') as f:
    
    f.write(f"")
    while True:

        line_a = hand.readline()

        line_b = eye.readline()

        if not line_a and not line_b:

            break

        if line_a:

            f.write(line_a)

        if line_b:

            f.write(line_b)


# input_file = 'target_to_cam.txt'
# output_file = 'eye.txt'

# with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
#     for line in f_in:
#         parts = line.strip().split()
        
#         f_out.write(','.join(parts) + '\n')
