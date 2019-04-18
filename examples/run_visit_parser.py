"""Examples for running and using the JWST visit file parser.

Authors
-------
    Johannes Sahlmann


"""
import glob
import os

import astropy.units as u

from visit_parser import parse_visit_file


local_dir = os.path.dirname(os.path.abspath(__file__))
test_data_dir = os.path.join(local_dir, 'test_data')


check_siaf_update = True
write_niriss_reports = True
# write_niriss_reports = False

if check_siaf_update:
    # compare pointing information before and after SIAF update
    print('^' * 100)
    import pysiaf
    siaf = pysiaf.Siaf('fgs')
    v2_0 = None
    v3_0 = None

    # test location in the sky
    ra = 80.349
    dec = -69.5456

    for visit_id in 'V00744008001_1910201f02 V00744008001_1910201f03'.split():
        visit_file = os.path.join(test_data_dir, 'siaf_update', '{}.vst'.format(visit_id))
        print(os.path.basename(visit_file))
        visit = parse_visit_file(visit_file)

        for statement in visit.script_statements:
            if statement.scriptname == 'FGSMAIN':
                fgs_statement = statement

                aperture_name = 'FGS{}_FULL_OSS'.format(fgs_statement.DETECTOR[-1])
                aperture = siaf[aperture_name]
                v2, v3 = aperture.idl_to_tel(fgs_statement.GSXSCI, fgs_statement.GSYSCI)
                try:
                    gsra = fgs_statement.GSRA
                    gsdec = fgs_statement.GSDEC
                    gsra_group = gsra
                    gsdec_group = gsdec
                except AttributeError:
                    gsra = gsra_group
                    gsdec = gsdec_group

                attitude = pysiaf.rotations.attitude(v2, v3, gsra, gsdec, fgs_statement.GSROLLSCI)
                v2_test, v3_test = pysiaf.rotations.sky_to_tel(attitude, ra, dec)
                print('Pointing of RA={:2.5f}, Dec={:2.5f} is v2={:+08.3f}  v3={:+08.3f}'.format(ra, dec, v2_test.to(u.arcsec), v3_test.to(u.arcsec)))
                if v2_0 is None:
                    v2_0 = v2_test
                    v3_0 = v3_test
                else:
                    print('Pointing difference is                   dv2={:+08.3f} dv3={:+08.3f}'.format((v2_test-v2_0).to(u.arcsec),
                                                                                              (v3_test-v3_0).to(u.arcsec)))

                break  # look at the first guide star only
    print('^' * 100)


if write_niriss_reports:
    out_dir = os.path.join(test_data_dir, 'niriss', 'out')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for visit_file in glob.glob(os.path.join(test_data_dir, 'niriss', '*.vst')):
        print(visit_file)
        visit = parse_visit_file(visit_file)
        visit.table.pprint()
        niriss_table = visit.overview_table(instrument='niriss')
        niriss_table.write(os.path.join(out_dir, '{}_visit_file_summary.txt'.format(visit.id)),
                           format='ascii.fixed_width', delimiter=',', bookend=False)


