from __future__ import print_function

from ConfigParser import NoSectionError

from ... import profile
from ...util.format.table import simple
from ...util.input.qna import QnA
from ..showall.__main__ import findall as show_all_profile

def print_as_table(profile_name, config):
    print(simple.show('%s.%s' % (profile_name, config.__name__),
        sorted(vars(config).items())))

def ask_profile(option, section=None):
    candidates = show_all_profile(option)
    if candidates:
        if len(candidates) == 1:
            print('Or did you mean `{}`?'.format(candidates[0]), end='\n\n')
            return print_profile(candidates[0], section=section)
        print('Found possible profiles.')
        item_range = range(len(candidates))
        print('    ',
                *['(%s) %s' % (index+1, candy)
                    for index, candy in enumerate(candidates)],
            sep='\n    ', end='\n\n')
        qna = QnA('Which one? (1-%d), others to quit: ' % len(candidates)).ask()
        ans = qna.answer
        if ans and ans.isdigit() and int(ans)-1 in item_range:
            print('')
            prof = candidates[int(ans)-1]
            print_profile(prof, section=section)

def print_profile(profile_name, section=None):
    try:
        Profile = profile.manager.get(profile_name.replace('-', '_'))
        if Profile.is_empty:
            raise
        if section:
            config = Profile.section(section)
            print_as_table(profile_name, config)
        else:
            for config in Profile:
                print_as_table(profile_name, config)
    except NoSectionError as e:
        print('Profile `{}` has no `{}` section.'.format(profile_name, section))
    except Exception as e:
        print('Unable to locate the profile `%s`.' % profile_name)
        ask_profile(profile_name, section=section)

def print_current():
    for profile_name, Profile in profile.manager.items():
        config = Profile.as_resolved
        print_as_table(profile_name, config)

def main(option, section):
    if not option and not section:
        return print_current()
    print_profile(option, section)

if __name__ == '__api_main__':
    if edit:
        profile.manager.get(edit).vim()
    else:
        main(option, section)
