# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'CategoryLog.n_overlay'
        db.add_column('euscan_categorylog', 'n_overlay', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Package.n_overlay'
        db.add_column('euscan_package', 'n_overlay', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'HerdLog.n_overlay'
        db.add_column('euscan_herdlog', 'n_overlay', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'MaintainerLog.n_overlay'
        db.add_column('euscan_maintainerlog', 'n_overlay', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'CategoryLog.n_overlay'
        db.delete_column('euscan_categorylog', 'n_overlay')

        # Deleting field 'Package.n_overlay'
        db.delete_column('euscan_package', 'n_overlay')

        # Deleting field 'HerdLog.n_overlay'
        db.delete_column('euscan_herdlog', 'n_overlay')

        # Deleting field 'MaintainerLog.n_overlay'
        db.delete_column('euscan_maintainerlog', 'n_overlay')


    models = {
        'euscan.categorylog': {
            'Meta': {'object_name': 'CategoryLog'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'n_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packaged': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packages': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
            'Meta': {'object_name': 'HerdLog'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'herd': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['euscan.Herd']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'n_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packaged': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packages': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'euscan.maintainer': {
            'Meta': {'object_name': 'Maintainer'},
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'euscan.maintainerlog': {
            'Meta': {'object_name': 'MaintainerLog'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['euscan.Maintainer']"}),
            'n_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packaged': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packages': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'euscan.package': {
            'Meta': {'unique_together': "(['category', 'name'],)", 'object_name': 'Package'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'herds': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['euscan.Herd']", 'symmetrical': 'False', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['euscan.Maintainer']", 'symmetrical': 'False', 'blank': 'True'}),
            'n_overlay': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_packaged': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'n_versions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'euscan.version': {
            'Meta': {'unique_together': "(['package', 'slot', 'revision', 'version', 'overlay'],)", 'object_name': 'Version'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overlay': ('django.db.models.fields.CharField', [], {'default': "'gentoo'", 'max_length': '128'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['euscan.Package']"}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'urls': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['euscan']
