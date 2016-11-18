from __future__ import absolute_import
import time
from bokeh.io import gridplot
from bokeh.embed import autoload_server
from bokeh.client import push_session
from bokeh.models.formatters import TickFormatter, MyFormatter
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, HoverTool, FixedTicker, TapTool, OpenURL, ResetTool, BoxZoomTool
from bokeh.models.layouts import Column
import subprocess
import pandas as pd
from math import pi
from bokeh.core.properties import Int, Float, Seq, Instance, Override, Dict, String



def follow(thefile):
	thefile.seek(0,2)
	while True:
		line = thefile.readline()
		if not line:
			time.sleep(0.1)
			continue
		yield line

def frange(start, stop, step):
	i = start
	while i < stop:
		yield i
		i += step

def prepare_data(specie):
	print(specie)

	species = specie.keys()
	nReads = specie.values()
	left_edge = list(frange(-0.3, len(specie)-1, 1))
	right_edge = list(frange(0.3, len(specie), 1))
 	df =  pd.DataFrame.from_items([('species', species), ('reads', nReads), 
 								   ('left', left_edge), ('right', right_edge)])
	print(df)
	return df, species

def update(specie, source, plot):
	"""Stream new data to the species plot."""
	df, species = prepare_data(specie)
	source.data = dict(
		reads = df['reads'],
		species = df['species'],
		left_edge = df['left'],
		right_edge = df['right']
		)
	print(species)
	# Format the labels on the x axis to print the species name.
	plot.xaxis[0].formatter = MyFormatter(labels=species)


def update_reads(read_source, basecalled, basecalled_times, no_basecalled, no_basecalled_times):
	"""Stream new data to the basecalled/no basecalled plot"""
	new_data = dict(
		basecalled = [basecalled[-1]],
		basecalled_times = [basecalled_times[-1]],
		no_basecalled = [no_basecalled[-1]],
		no_basecalled_times = [no_basecalled_times[-1]])
	print(new_data)
	
	read_source.stream(new_data, 300)

def update_hits(hits_source, species, hits, time, hits_basecalled):
	new_data = dict(
		hits = [hits[-1]],
		species = [species[-1]],
		times = [time[-1]],
		hits_basecalled = [hits_basecalled[-1]])
	print(new_data)
	hits_source.stream(new_data, 300)

def hit_plot(source):
	hover = HoverTool(tooltips=[('Specie', '@species')])
	hover.point_policy = "follow_mouse"
	plot = figure(title="Hits", plot_width=800, plot_height = 400, tools=[hover])
	plot.circle('times', 'hits', size=10, source=hits_source)

	return plot


def bar_plot(source):

	plot = figure(title="Species", x_range=(-1, 20), y_range=(0,5), plot_width = 800, plot_height = 400, tools="tap")

	plot.quad(top='reads', bottom=0, left='left_edge', right='right_edge',
		      fill_color='#036463', line_color="#033649", source=source)
	plot.xaxis.major_label_orientation = pi/2
	#plot.xaxis.major_label_text_baseline = 
	plot.xaxis.major_label_standoff = 10
	plot.xaxis.major_label_text_font_size = "14pt"
	plot.xaxis[0].ticker.desired_num_ticks = 20
	# Remove all labels on the x-axis. DOES NOT WORK.
	#plot.xaxis[0].formatter = MyFormatter(labels=[])

	url = "https://www.google.se/#q=@species"

	taptool = plot.select(type=TapTool)
	taptool.callback = OpenURL(url=url)
	return plot

def read_plot(read_source, hits_source):
	hover = HoverTool(tooltips=[('Specie', '@species')])
	hover.point_policy = "follow_mouse"
	tools = [hover, ResetTool(), BoxZoomTool()]
	plot = figure(title='Reads', plot_width = 800, plot_height = 500, tools=tools, toolbar_location='above')
	plot.line('basecalled_times', 'basecalled', legend='Basecalled', line_width=3, source=read_source)
	plot.circle('basecalled_times', 'basecalled', size=6, source=read_source)
	plot.line('no_basecalled_times', 'no_basecalled', legend='Not basecalled', line_width=3, color='firebrick', source=read_source)
	plot.circle('no_basecalled_times', 'no_basecalled', color='firebrick', size=6, source=read_source)
	circle = plot.circle('times', 'hits_basecalled', fill_color='white', line_width=3, size=12, source=hits_source)
	plot.tools[0].renderers.append(circle)
	plot.xaxis[0].axis_label = 'Time since start (S)'
	plot.yaxis[0].axis_label = 'Number of sequences'
	plot.legend.location = 'top_left'
	return plot

def draw_plot(source, read_source, hits_source):
	bar = bar_plot(source)
	print('Bar plot created')
	readOverTime = read_plot(read_source, hits_source)
	print('Reads plot created')
	hit = hit_plot(hits_source)
	print('Hit plot created')
	layout = Column(readOverTime, bar)
	session = push_session(curdoc())
	session.show(layout)

	return bar


if __name__ == '__main__':
	plotfile = open('outfile.txt', 'r')
	loglines = follow(plotfile)
	subprocess.Popen(['bokeh', 'serve'], shell=False)
	time.sleep(2)
	specie = {}
	basecalled = [0]
	no_basecalled = [0]
	basecalled_times = [0]
	no_basecalled_times = [0]
	hits_specie = [0]
	hits_time = [0]
	nr_hits = [0]
	source = ColumnDataSource(data=dict(reads=[], species=[], left_edge=[], right_edge=[]))
	read_source = ColumnDataSource(data=dict(basecalled=[], basecalled_times=[], no_basecalled=[], no_basecalled_times=[]))
	hits_source = ColumnDataSource(data=dict(hits=[], species=[], times=[], hits_basecalled=[]))
	plot = draw_plot(source, read_source, hits_source)
	update_reads(read_source, basecalled, basecalled_times, no_basecalled, no_basecalled_times)
	for line in loglines:
		print(line)
		line = line.split(";")
		if line[0] == 'Read':
			print('New Read')
			if line[2].strip() == 'basecalled':
				basecalled.append(basecalled[-1] + 1)
				basecalled_times.append(line[1])
			else:
				no_basecalled.append(no_basecalled[-1] + 1)
				no_basecalled_times.append(line[1])
			update_reads(read_source, basecalled, basecalled_times, no_basecalled, no_basecalled_times)
		else:	
			specie[line[0]] = int(line[1])
			nr_hits.append(nr_hits[-1] + 1)
			hits_time.append(int(line[2].strip()))
			hits_specie.append(line[0])
			hits_basecalled = basecalled
			update_hits(hits_source, hits_specie, nr_hits, hits_time, hits_basecalled)
			update(specie, source, plot)
		
