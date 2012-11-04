# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('djeuscan_userprofile',
                        'euscan_accounts_userprofile')
        db.rename_table('djeuscan_userprofile_overlays',
                        'euscan_accounts_userprofile_overlays')
        db.rename_table('djeuscan_userprofile_maintainers',
                        'euscan_accounts_userprofile_maintainers')
        db.rename_table('djeuscan_userprofile_packages',
                        'euscan_accounts_userprofile_packages')
        db.rename_table('djeuscan_userprofile_herds',
                        'euscan_accounts_userprofile_herds')
        db.rename_table('djeuscan_userprofile_categories',
                        'euscan_accounts_userprofile_categories')

        if not db.dry_run:
            # For permissions to work properly after migrating
            orm['contenttypes.contenttype'].objects.filter(
                app_label='djeuscan', model='userprofile'
            ).update(app_label='euscan_accounts')

    def backwards(self, orm):
        db.rename_table('euscan_accounts_userprofile',
                        'djeuscan_userprofile')
        db.rename_table('euscan_accounts_userprofile_overlays',
                        'djeuscan_userprofile_overlays')
        db.rename_table('euscan_accounts_userprofile_maintainers',
                        'djeuscan_userprofile_maintainers')
        db.rename_table('euscan_accounts_userprofile_packages',
                        'djeuscan_userprofile_packages')
        db.rename_table('euscan_accounts_userprofile_herds',
                        'djeuscan_userprofile_herds')
        db.rename_table('euscan_accounts_userprofile_categories',
                        'djeuscan_userprofile_categories')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djeuscan.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'djeuscan.herd': {
            'Meta': {'object_name': 'Herd'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'herd': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Maintainer']", 'symmetrical': 'False'})
        },
        'djeuscan.maintainer': {
            'Meta': {'object_name': 'Maintainer'},
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djeuscan.overlay': {
            'Meta': {'object_name': 'Overlay'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'djeuscan.package': {
            'Meta': {'unique_together': "(['category', 'name'],)", 'object_name': 'Package'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'herds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Herd']", 'symmetrical': 'False', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_version_gentoo': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_gentoo'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['djeuscan.Version']"}),
            'last_version_overlay': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_overlay'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['djeuscan.Version']"}),
            'last_version_upstream': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_upstream'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['djeuscan.Version']"}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Maintainer']", 'symmetrical': 'False', 'blank': 'True'}),
            'n_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packaged': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djeuscan.version': {
            'Meta': {'unique_together': "(['package', 'slot', 'revision', 'version', 'overlay'],)", 'object_name': 'Version'},
            'alive': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'confidence': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ebuild_path': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'handler': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata_path': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'overlay': ('django.db.models.fields.CharField', [], {'default': "'gentoo'", 'max_length': '128', 'db_index': 'True', 'blank': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slot': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'urls': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'vtype': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'euscan_accounts.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Category']", 'symmetrical': 'False'}),
            'email_activated': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'email_every': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'email_ignore_pre': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_ignore_pre_if_stable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'feed_ignore_pre': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'feed_ignore_pre_if_stable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'feed_portage_info': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'feed_show_adds': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'feed_show_removals': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'feed_upstream_info': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'herds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Herd']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_email': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Maintainer']", 'symmetrical': 'False'}),
            'overlays': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Overlay']", 'symmetrical': 'False'}),
            'packages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Package']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['euscan_accounts']
