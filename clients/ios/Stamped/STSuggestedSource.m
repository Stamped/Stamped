//
//  STSuggestedSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSuggestedSource.h"
#import "STStampedAPI.h"
#import "Util.h"
#import "STSearchField.h"

@implementation STSuggestedSource

- (void)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice andCallback:(void (^)(NSArray<STStamp>*, NSError*))block {
  [[STStampedAPI sharedInstance] stampsForSuggestedSlice:slice andCallback:block];
}

- (NSString *)lastCellText {
  if (!self.slice.query) {
    return @"No Stamps available right now";
  }
  else {
    return [NSString stringWithFormat:@"Search for %@", self.slice.query];
  }
}

- (NSString *)noStampsText {
  return self.lastCellText;
}

- (void)selectedLastCell {
  if (!self.slice.query) {
  }
  else {
    /*
     TODO repair
    SearchEntitiesViewController* search = [[[SearchEntitiesViewController alloc] initWithNibName:@"SearchEntitiesViewController" bundle:nil] autorelease];
    UINavigationController* controller = [Util sharedNavigationController];
    [controller pushViewController:search
                          animated:YES];
     */
  }
}

- (void)selectedNoStampsCell {
  [self selectedLastCell];
}

@end
