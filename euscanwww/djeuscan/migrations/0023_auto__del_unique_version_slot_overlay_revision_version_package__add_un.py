# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Version', fields ['slot', 'overlay', 'revision', 'version', 'package']
        db.delete_unique('djeuscan_version', ['slot', 'overlay', 'revision', 'version', 'package_id'])

        # Adding unique constraint on 'Version', fields ['overlay', 'revision', 'version', 'package']
        db.create_unique('djeuscan_version', ['overlay', 'revision', 'version', 'package_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'Version', fields ['overlay', 'revision', 'version', 'package']
        db.delete_unique('djeuscan_version', ['overlay', 'revision', 'version', 'package_id'])

        # Adding unique constraint on 'Version', fields ['slot', 'overlay', 'revision', 'version', 'package']
        db.create_unique('djeuscan_version', ['slot', 'overlay', 'revision', 'version', 'package_id'])

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
        'djeuscan.categorylog': {
            'Meta': {'object_name': 'CategoryLog', '_ormbases': ['djeuscan.Log']},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        },
        'djeuscan.euscanresult': {
            'Meta': {'object_name': 'EuscanResult'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'ebuild': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'result': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'scan_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'djeuscan.herd': {
            'Meta': {'object_name': 'Herd'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'herd': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['djeuscan.Maintainer']", 'symmetrical': 'False'})
        },
        'djeuscan.herdlog': {
            'Meta': {'object_name': 'HerdLog', '_ormbases': ['djeuscan.Log']},
            'herd': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Herd']"}),
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        },
        'djeuscan.log': {
            'Meta': {'object_name': 'Log'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'n_packages_gentoo': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packages_outdated': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packages_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions_gentoo': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions_upstream': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'djeuscan.maintainer': {
            'Meta': {'object_name': 'Maintainer'},
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'djeuscan.maintainerlog': {
            'Meta': {'object_name': 'MaintainerLog', '_ormbases': ['djeuscan.Log']},
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'}),
            'maintainer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Maintainer']"})
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
        'djeuscan.problemreport': {
            'Meta': {'object_name': 'ProblemReport'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Version']", 'null': 'True', 'blank': 'True'})
        },
        'djeuscan.refreshpackagequery': {
            'Meta': {'object_name': 'RefreshPackageQuery'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'djeuscan.version': {
            'Meta': {'unique_together': "(['package', 'revision', 'version', 'overlay'],)", 'object_name': 'Version'},
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
        'djeuscan.versionlog': {
            'Meta': {'object_name': 'VersionLog'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overlay': ('django.db.models.fields.CharField', [], {'default': "'gentoo'", 'max_length': '128', 'blank': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djeuscan.Package']"}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slot': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'vtype': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'djeuscan.worldlog': {
            'Meta': {'object_name': 'WorldLog', '_ormbases': ['djeuscan.Log']},
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['djeuscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['djeuscan']