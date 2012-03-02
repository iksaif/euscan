# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Package.last_version_gentoo'
        db.add_column('euscan_package', 'last_version_gentoo', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_version_gentoo', null=True, to=orm['euscan.Version']), keep_default=False)

        # Adding field 'Package.last_version_overlay'
        db.add_column('euscan_package', 'last_version_overlay', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_version_overlay', null=True, to=orm['euscan.Version']), keep_default=False)

        # Adding field 'Package.last_version_upstream'
        db.add_column('euscan_package', 'last_version_upstream', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_version_upstream', null=True, to=orm['euscan.Version']), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Package.last_version_gentoo'
        db.delete_column('euscan_package', 'last_version_gentoo_id')

        # Deleting field 'Package.last_version_overlay'
        db.delete_column('euscan_package', 'last_version_overlay_id')

        # Deleting field 'Package.last_version_upstream'
        db.delete_column('euscan_package', 'last_version_upstream_id')


    models = {
        'euscan.categorylog': {
            'Meta': {'object_name': 'CategoryLog', '_ormbases': ['euscan.Log']},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['euscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        },
        'euscan.euscanresult': {
            'Meta': {'object_name': 'EuscanResult'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['euscan.Package']"}),
            'result': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'euscan.herd': {
            'Meta': {'object_name': 'Herd'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'herd': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'euscan.herdlog': {
            'Meta': {'object_name': 'HerdLog', '_ormbases': ['euscan.Log']},
            'herd': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['euscan.Herd']"}),
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['euscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        },
        'euscan.log': {
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
        'euscan.maintainer': {
            'Meta': {'object_name': 'Maintainer'},
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'euscan.maintainerlog': {
            'Meta': {'object_name': 'MaintainerLog', '_ormbases': ['euscan.Log']},
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['euscan.Log']", 'unique': 'True', 'primary_key': 'True'}),
            'maintainer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['euscan.Maintainer']"})
        },
        'euscan.package': {
            'Meta': {'unique_together': "(['category', 'name'],)", 'object_name': 'Package'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'herds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['euscan.Herd']", 'symmetrical': 'False', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_version_gentoo': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_gentoo'", 'null': 'True', 'to': "orm['euscan.Version']"}),
            'last_version_overlay': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_overlay'", 'null': 'True', 'to': "orm['euscan.Version']"}),
            'last_version_upstream': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_version_upstream'", 'null': 'True', 'to': "orm['euscan.Version']"}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['euscan.Maintainer']", 'symmetrical': 'False', 'blank': 'True'}),
            'n_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packaged': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'euscan.version': {
            'Meta': {'unique_together': "(['package', 'slot', 'revision', 'version', 'overlay'],)", 'object_name': 'Version'},
            'alive': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overlay': ('django.db.models.fields.CharField', [], {'default': "'gentoo'", 'max_length': '128', 'db_index': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['euscan.Package']"}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'urls': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'euscan.versionlog': {
            'Meta': {'object_name': 'VersionLog'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 2, 16, 32, 3, 656974)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overlay': ('django.db.models.fields.CharField', [], {'default': "'gentoo'", 'max_length': '128'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['euscan.Package']"}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'euscan.worldlog': {
            'Meta': {'object_name': 'WorldLog', '_ormbases': ['euscan.Log']},
            'log_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['euscan.Log']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['euscan']
