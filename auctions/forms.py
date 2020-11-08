from django.forms import ModelForm
from auctions.models import Listing, Bid, Comment

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_price', 'image', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'create'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Submit'))

class NewBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bid_price"].widget.attrs["placeholder"] = "Enter bid"
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'place_bid'
        self.helper.form_show_labels = False
        self.helper.field_class = 'col-lg-2'
        self.helper.add_input(Submit('submit', 'Place Bid'))

class NewCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].widget.attrs["placeholder"] = "Enter a comment here..."
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'create_comment'
        self.helper.form_show_labels = False
        self.helper.field_class = 'col-lg-4'
        self.helper.add_input(Submit('submit', 'Comment'))



