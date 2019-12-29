def choice(idx):
    if idx <= 4:
        return {
            'type': 'move',
            'id': str(idx),
            'modifier': '',
            }
    return {
        'type': 'switch',
        'id': str(idx-4),
        'modifier': '',
        }
