from django import forms

Genome_Formats = [
                  ('GENBANK', 'Genbank'),
                  ('EMBL', 'Embl')
                  ]

class UploadGenomeForm(forms.Form):
    format_type = forms.ChoiceField(choices=Genome_Formats, widget=forms.Select(attrs={"onChange":'changeFileType()'}))
    genome_name = forms.CharField(max_length=59, required=False, label="Genome name (optional)", widget=forms.TextInput( attrs={'size':'40'} ))                                                                         
    email_addr = forms.EmailField(max_length=80, required=False, label="Email address to be notified upon completion (optional)", widget=forms.TextInput( attrs={'size':'40'} ))
    cid = forms.IntegerField(widget=forms.HiddenInput(), required=False, initial=0)
    ref_accnum = forms.CharField(widget=forms.HiddenInput(), required=False, initial=False)
    genome_file  = forms.FileField()
