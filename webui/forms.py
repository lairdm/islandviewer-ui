from django import forms

Genome_Formats = [
                  ('GENBANK', 'Genbank'),
                  ('EMBL', 'Embl')
                  ]

class UploadGenomeForm(forms.Form):
    format_type = forms.ChoiceField(choices=Genome_Formats, widget=forms.Select(attrs={"onChange":'changeFileType()'}))
    genome_name = forms.CharField(max_length=50, required=False, label="Genome name (optional)")
    email_addr = forms.EmailField(required=False, label="Email address to be notified upon completion (optional)")
    genome_file  = forms.FileField()
