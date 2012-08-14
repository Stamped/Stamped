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
#import "STEntitySearchController.h"

@implementation STSuggestedSource

- (STCancellation*)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice 
                                   andCallback:(void (^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
    return [[STStampedAPI sharedInstance] stampsForSuggestedSlice:slice andCallback:block];
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
        [Util pushController:[[[STEntitySearchController alloc] initWithCategory:self.slice.category
                                                                        andQuery:self.slice.query] autorelease]
                       modal:NO
                    animated:YES];
    }
}

- (void)selectedNoStampsCell {
    [self selectedLastCell];
}

@end
