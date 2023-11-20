def is_termination_msg(content):
    have_content = content.get('content', None) is not None
    if have_content and 'END' in content['content']:
        return True
    return False

        
