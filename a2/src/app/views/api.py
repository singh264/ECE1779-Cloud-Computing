
##################################################
# This file contains JSON return codes.
# The actual API endpoint implementations are colocated
# with their GUI counterparts.
#
##################################################

def api_error_json(code, message):
    d = {
        'success': False,
        'error': {
            'code': code,
            'message': message
        }
    }
    return d

def api_register_json():
    d = {
        'success': True
    }
    return d

def api_upload_json(num_faces, num_masked, num_unmasked):
    d = {
        'success': True,
        'payload': {
            'num_faces': num_faces,
            'num_masked': num_masked,
            'num_unmasked': num_unmasked
        }
    }
    return d

