# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'CategoryLog'
        db.delete_table('euscan_categorylog')

        # Deleting model 'HerdLog'
        db.delete_table('euscan_herdlog')

        # Deleting model 'MaintainerLog'
        db.delete_table('euscan_maintainerlog')

        # Adding model 'Log'
        db.create_table('euscan_log', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('n_packages_gentoo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_packages_overlay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_packages_outdated', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_gentoo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_overlay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_upstream', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('euscan', ['Log'])


    def backwards(self, orm):
        
        # Adding model 'CategoryLog'
        db.create_table('euscan_categorylog', (
            ('category', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('n_packages_gentoo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_packages_outdated', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_packages_overlay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_upstream', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_overlay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_gentoo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('euscan', ['CategoryLog'])

        # Adding model 'HerdLog'
        db.create_table('euscan_herdlog', (
            ('n_packages_gentoo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_overlay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_packages_outdated', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_packages_overlay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_upstream', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('herd', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['euscan.Herd'])),
            ('n_versions_gentoo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('euscan', ['HerdLog'])

        # Adding model 'MaintainerLog'
        db.create_table('euscan_maintainerlog', (
            ('n_packages_gentoo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_overlay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_packages_outdated', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maintainer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['euscan.Maintainer'])),
            ('n_packages_overlay', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_upstream', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('n_versions_gentoo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('euscan', ['MaintainerLog'])

        # Deleting model 'Log'
        db.delete_table('euscan_log')


    models = {
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
