class EvaluationParser:
    def __init__(self, soup):
        self._soup = soup
        self.inputs = []

    def parse(self):
        form = self._soup.select('#frm_evaluation')[0]
        radios = {}
        for i in form.select('input'):
            input = {
                'type': i['type'],
                'name': i['name'],
                'value': i['value'],
                'checked': 'checked' in i.attrs,
                'disabled': 'disabled' in i.attrs
            }

            if input['type'] == 'radio':
                if input['name'] not in radios:
                    radios[input['name']] = []
                radios[input['name']].append(input)
            else:
                self.inputs.append(input)
        
        for k,v in radios.items():
            input = {
                'type': 'radio',
                'name': k,
                'value': None,
                'disabled': False,
                'options': []
            }
            for r in v:
                if r['checked']:
                    input['value'] = r['value']
                if r['disabled']:
                    input['disabled'] = True
                input['options'].append(r['value'])
            self.inputs.append(input)
        
        for textarea in form.select('textarea'):
            self.inputs.append({
                'type': 'textarea',
                'name': textarea['name'],
                'value': textarea.text,
                'disabled': 'disabled' in textarea.attrs
            })
        

        
    
        

        