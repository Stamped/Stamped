//
//  STRdioPlaylistPopUp.m
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRdioPlaylistPopUp.h"
#import "STRdio.h"

@implementation STRdioPlaylistPopUp


- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  id<STPlaylistItem> item = [self.playlistItems objectAtIndex:indexPath.row];
  NSString* itemID = [self getItemId:item];
  if (itemID) {
    [[STRdio sharedRdio] startPlayback:itemID];
  }
  else {
    NSAssert(NO, @"rdio id was null");
  }
  NSLog(@"selected item:%@", item.name);
}

- (void)didMoveToSuperview {
  [super didMoveToSuperview];
  if (self.superview == nil) {
    [[STRdio sharedRdio] stopPlayback];
  }
}

- (NSString*)getItemId:(id<STPlaylistItem>)item {
  if (item.action.sources.count) {
    for (id<STSource> source in item.action.sources) {
      if ([source.source isEqualToString:@"rdio"]) {
        return source.sourceID;
      }
    }
  }
  return nil;
}

@end
