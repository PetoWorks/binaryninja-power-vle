from powervle.decoder import *


if __name__ == "__main__":
    hexint = lambda x: int(x, 16)
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--start", type=hexint, default=-1)
    parser.add_argument("--length", type=hexint, default=-1)
    parser.add_argument("--print", action='store_true')
    args = parser.parse_args()

    with open(args.file, 'rb') as f:
        if args.start >= 0:
            f.seek(args.start)
        if args.length >= 0:
            data = f.read(args.length)
        else:
            data = f.read()
    
    if len(data) % 4:
        data += b'\x00' * (4 - len(data) % 4)
    
    counter = {}
    
    from io import BytesIO
    bio = BytesIO(data)
    while (cur := bio.read(4)):

        inst = Decoder.decode(cur, categories=("VLE", ))
        if inst.name not in counter:
            counter[inst.name] = 0
        counter[inst.name] += 1

        if inst.length == 2:
            bio.seek(-2, 1) if len(cur) > 2 else None
            if args.print:
                data = int.from_bytes(cur[:2], 'big')
                print(f"{data:04x}      {inst.name}")
        elif inst.length == 4:
            if args.print:
                data = int.from_bytes(cur, 'big')
                print(f"{data:08x}  {inst.name}")
        else:
            raise ValueError

    name_max_len = len(max(counter.keys(), key=len))

    for k, v in sorted(counter.items(), key=lambda item: item[1], reverse=True):
        print(k.ljust(name_max_len) + " : " + str(v))
