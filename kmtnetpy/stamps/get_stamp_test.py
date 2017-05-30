from kmtnetpy.stamps.get_stamp import get_stamps_from_key


if 1:
    l1 = {'filename_key': (u'E489-1', 'Q1', u'B', u'160125_0529',
                           'C', u'049062'),
          'id': u'20160125-ctio-000138'}

    xy_list = [(176 - 1, 9125 - 1),
               (16 - 1, 9195 - 1)]

    im_list = get_stamps_from_key(l1["filename_key"], xy_list, size=64)
