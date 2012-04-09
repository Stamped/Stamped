//
//  STPlaylistViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 4/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STPlaylistViewFactory.h"
#import "STViewContainer.h"

@interface STPlaylistItemView : UIView

- (id)initWithPlaylistItem:(id<STPlaylistItem>)playlistItem 
              entityDetail:(id<STEntityDetail>)entityDetail 
               andDelegate:(id<STViewDelegate>)delegate;

@end

@implementation STPlaylistItemView

- (id)initWithPlaylistItem:(id<STPlaylistItem>)playlistItem 
              entityDetail:(id<STEntityDetail>)entityDetail 
               andDelegate:(id<STViewDelegate>)delegate {
  self = [super initWithFrame:CGRectMake(0, 0, 300, 50)];
  if (self) {
    self.backgroundColor = [UIColor greenColor];
  }
  return self;
}

@end

@interface STPlaylistView : STViewContainer

- (id)initWithEntityDetail:(id<STEntityDetail>)entityDetail andDelegate:(id<STViewDelegate>)delegate;

@end

@implementation STPlaylistView

- (id)initWithEntityDetail:(id<STEntityDetail>)entityDetail andDelegate:(id<STViewDelegate>)delegate {
  self = [super initWithFrame:CGRectMake(10, 0, 300, 0)];
  if (self) {
    if ([entityDetail.playlist.data count] > 0) {
      for (id<STPlaylistItem> item in entityDetail.playlist.data) {
        STPlaylistItemView* itemView = [[[STPlaylistItemView alloc] initWithPlaylistItem:item 
                                                                            entityDetail:entityDetail 
                                                                             andDelegate:self] autorelease];
        [self appendChildView:itemView];
      }
    }
  }
  return self;
}

@end

@implementation STPlaylistViewFactory

- (id)generateAsynchronousState:(id<STEntityDetail>)anEntityDetail withOperation:(NSOperation*)operation {
  return nil;
}

- (UIView*)generateViewOnMainLoop:(id<STEntityDetail>)anEntityDetail
                        withState:(id)asyncState
                      andDelegate:(id<STViewDelegate>)delegate {
  return [[[STPlaylistView alloc] initWithEntityDetail:anEntityDetail andDelegate:delegate] autorelease];
}

@end
