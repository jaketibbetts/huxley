from django import forms

from cms.models import *
from django.contrib.auth.models import User

import re

countries = Country.objects.filter(special=False).order_by('name')
country_choices = [(country.id, country.name) for country in countries]

special_committees = Committee.objects.filter(special=True)
special_committees_choices = [(committee.id, committee.name) for committee in special_committees]

class RegistrationForm(forms.Form):
    # By default, fields are required unless you specify required=False

    # User Information
    FirstName = forms.CharField(label="First Name", widget=forms.TextInput(attrs={'class':'half required'}))
    LastName = forms.CharField(label="Last Name", widget=forms.TextInput(attrs={'class':'half required'}))
    Username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class':'half required uniqueUser username'}), min_length=4)
    Password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class':'half required pass1 validChars'}), min_length=6)
    Password2 = forms.CharField(label="Password (again)", widget=forms.PasswordInput(attrs={'class':'half required pass1 validChars'}))

    # School Information
    # TODO: Pick a default for international
    us_or_int = forms.ChoiceField(label="Where is your school?", widget=forms.RadioSelect(attrs={'class':'int_check', 'name':'us_or_int'}), choices=(('us', 'United States'), ('international', 'International')))
    SchoolName = forms.CharField(label="Official School Name", widget=forms.TextInput(attrs={'class':'full required'}))
    SchoolAddress = forms.CharField(label="Address", widget=forms.TextInput(attrs={'class':'full required'}))
    SchoolCity = forms.CharField(label="City", widget=forms.TextInput(attrs={'class':'required'}))
    SchoolState = forms.CharField(label="State", widget=forms.TextInput(attrs={'class':'required'}))
    SchoolZip = forms.CharField(label="Zip", widget=forms.TextInput(attrs={'class':'required zip'}), min_length=5)
    SchoolCountry = forms.CharField(label="Country", widget=forms.TextInput(attrs={'class':'showhide'}), required=False)

    # Program Information
    programtype = forms.ChoiceField(label="What category best describes your program?", widget=forms.RadioSelect, choices=(('club', 'Club'), ('class', 'Class')))
    howmany = forms.IntegerField(label="Approximately how many times has your program attended BMUN?", widget=forms.TextInput(attrs={'class':'required IntegersOnly'}))
    MinDelegation = forms.IntegerField(label="Minimum", widget=forms.TextInput(attrs={'class':'required IntegersOnly'}))
    MaxDelegation = forms.IntegerField(label="Maximum", widget=forms.TextInput(attrs={'class':'required IntegersOnly'}))

    # Contact Information
    PrimaryName = forms.CharField(label="Name", widget=forms.TextInput(attrs={'class':'required'}))
    PrimaryEmail = forms.EmailField(label="Email", widget=forms.TextInput(attrs={'class':'required email'}))
    PrimaryPhone = forms.CharField(label="Phone", widget=forms.TextInput(attrs={'class':'required phoneNum phoneVal'}))
    SecondaryName = forms.CharField(label="Name", widget=forms.TextInput(), required=False)
    SecondaryEmail = forms.EmailField(label="Email", widget=forms.TextInput(attrs={'class':'email'}), required=False)
    SecondaryPhone = forms.CharField(label="Phone", widget=forms.TextInput(attrs={'class':'phoneNum phoneVal'}), required=False)

    # Country Preferences (the ids)
    CountryPref1 = forms.ChoiceField(label="01", widget=forms.Select(), choices=country_choices)
    CountryPref2 = forms.ChoiceField(label="02", widget=forms.Select(), choices=country_choices)
    CountryPref3 = forms.ChoiceField(label="03", widget=forms.Select(), choices=country_choices)
    CountryPref4 = forms.ChoiceField(label="04", widget=forms.Select(), choices=country_choices)
    CountryPref5 = forms.ChoiceField(label="05", widget=forms.Select(), choices=country_choices)
    CountryPref6 = forms.ChoiceField(label="06", widget=forms.Select(), choices=country_choices)
    CountryPref7 = forms.ChoiceField(label="07", widget=forms.Select(), choices=country_choices)
    CountryPref8 = forms.ChoiceField(label="08", widget=forms.Select(), choices=country_choices)
    CountryPref9 = forms.ChoiceField(label="09", widget=forms.Select(), choices=country_choices)
    CountryPref10 = forms.ChoiceField(label="10", widget=forms.Select(), choices=country_choices)

    # Committee Preferences
    CommitteePrefs = forms.MultipleChoiceField(label="Special Committee Preferences", 
                                               widget=forms.CheckboxSelectMultiple(),
                                               choices=special_committees_choices,
                                               required=False)

    # ===== DB Functions ====================================================================
    def create_user(self):
        try:
            new_user = User.objects.create_user(self.cleaned_data['Username'], self.cleaned_data['PrimaryEmail'], self.cleaned_data['Password'])
            new_user.first_name = self.cleaned_data['FirstName']
            new_user.last_name = self.cleaned_data['LastName']
            new_user.save()
            return new_user
        except:
            print "> ERROR WHILE CREATING USER. REMEMBER TO VALIDATE FIRST."
            return None


    def create_school(self):
        try:
            new_school = School.objects.create(name=self.cleaned_data['SchoolName'],
                                               address=self.cleaned_data['SchoolAddress'],
                                               city=self.cleaned_data['SchoolCity'],
                                               state=self.cleaned_data['SchoolState'],
                                               zip=self.cleaned_data['SchoolZip'],
                                               primaryname = self.cleaned_data['PrimaryName'],
                                               primaryemail = self.cleaned_data['PrimaryEmail'],
                                               primaryphone = self.cleaned_data['PrimaryPhone'],
                                               secondaryname = self.cleaned_data['SecondaryName'],
                                               secondaryemail = self.cleaned_data['SecondaryEmail'],
                                               secondaryphone = self.cleaned_data['SecondaryPhone'],
                                               programtype = self.cleaned_data['programtype'],
                                               timesattended = self.cleaned_data['howmany'],
                                               mindelegationsize = self.cleaned_data['MinDelegation'],
                                               maxdelegationsize = self.cleaned_data['MaxDelegation'],
                                               international = self.cleaned_data['us_or_int'])
            new_school.save()
            return new_school
        except:
            print "> ERROR WHILE CREATING SCHOOL. REMEMBER TO VALIDATE FIRST."
            return None


    def add_country_preferences(self, school):
        try:
            for i in range(1,11):
                # TODO: try using country instead of id for value
                country_id = self.cleaned_data['CountryPref'+str(i)]
                country = Country.objects.get(id=int(country_id))
                country_pref = CountryPreference.objects.create(school=school, country=country, rank=i)
                country_pref.save()
            return True
        except:
            print "> ERROR WHILE ADDING COUNTRY PREFERENCES. REMEMBER TO VALIDATE FIRST."
            return False


    def add_committee_preferences(self, school):
        try:
            committees = self.cleaned_data["CommitteePrefs"]
            for committee_id in committees:
                committee = Committee.objects.get(id=int(committee_id))
                school.committeepreferences.add(committee)
            school.save()
            return True
        except:
            print "> ERROR WHILE ADDING COMMITTEE PREFERENCES. REMEMBER TO VALIDATE FIRST."
            return False


    def create_advisor_profile(self, user, school):
        try:
            new_profile = AdvisorProfile.objects.create(user=user, school=school)
            new_profile.save()
            return new_profile
        except:
            print "> ERROR WHILE MAKING ADVISOR PROFILE."
            return None


    # ===== Validation ===============================================================================
    # Format: clean_<field>
    def clean_SchoolName(self):
        # Check for uniqueness
        school_name = self.cleaned_data['SchoolName']
        unique = School.objects.filter(name = school_name).exists()
        if not unique:
            raise forms.ValidationError("A school with this name has already been registered.")
        # Return data, whether changed or not
        return school_name


    def clean_Username(self):
        # Check for uniqueness
        username = self.cleaned_data['Username']
        unique = User.objects.filter(username=username).exists()
        if not unique:
            raise forms.ValidationError("This username is already in use. Please choose another one.")
        # Make sure the characters are valid
        if re.match("^[A-Za-z0-9\_\-]+$", username) is None:
            raise forms.ValidationError("Usernames must be alphanumeric, underscores, and/or hyphens only.")
        # Return data, changed or not
        return username


    def clean_Password(self):
        password = self.cleaned_data['Password']
        if re.match("^[A-Za-z0-9\_\.!@#\$%\^&\*\(\)~\-=\+`\?]+$", password) is None:
            raise forms.ValidationError("Password contains invalid characters.") # TODO: make error message more informative
        # Return data, changed or not
        return password


    def phone_num_is_valid(self, number, international):
        if international == "international":
            if re.match("^[0-9\-x\s\+\(\)]+$", number):
                return True
            else:
                return False
        else:
            # Format: (123) 456-7890 || Note the space after the area code.
            if re.match("^\(?([0-9]{3})\)?\s([0-9]{3})-([0-9]{4})(\sx[0-9]{1,5})?$", number):
                return True
            else:
                return False


    # General clean method
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        Password = cleaned_data.get('Password')
        Password2 = cleaned_data.get('Password2')
        international = cleaned_data.get('us_or_int')
        primary_phone = cleaned_data.get('PrimaryPhone')
        secondary_phone = cleaned_data.get('SecondaryPhone')

        if Password and Password2 and Password != Password2:
            raise forms.ValidationError("Passwords must match!")

        if primary_phone and not self.phone_num_is_valid(primary_phone, international):
            raise forms.ValidationError("Phone in incorrect format. US Format: (XXX) XXX-XXXX")

        if secondary_phone and not self.phone_num_is_valid(secondary_phone, international):
            raise forms.ValidationError("Phone in incorrect format. US Format: (XXX) XXX-XXXX")

        # Checks for duplicates in country preferences
        countryprefs = set()
        for i in xrange(1,11):
            pref = cleaned_data["countrypref"+str(i)]
            if pref in countryprefs:
                raise forms.ValidationError("You can only choose a country once for your preferences.")
            countryprefs.add(pref)

        # Always return cleaned_data
        return cleaned_data
