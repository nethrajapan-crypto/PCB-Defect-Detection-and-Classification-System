import torch, json, sys
log_path = 'ckpt_check.log'
try:
    ckpt = torch.load('best_model.pth', map_location='cpu')
    info = {'type': str(type(ckpt)), 'keys': list(ckpt.keys())[:20] if isinstance(ckpt, dict) else None}
    with open(log_path, 'w') as f:
        json.dump(info, f, indent=2)
    print('OK')
except Exception as e:
    with open(log_path, 'w') as f:
        f.write('ERROR:\n')
        f.write(str(e))
    print('ERROR')
    sys.exit(1)
