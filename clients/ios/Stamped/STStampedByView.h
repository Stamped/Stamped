//
//  STStampedByView.h
//  Stamped
//
//  Created by Landon Judkins on 4/16/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStampedBy.h"
#import "STViewContainer.h"

@interface STStampedByView : STViewContainer

- (id)initWithStampedBy:(id<STStampedBy>)stampedBy blacklist:(NSSet*)blacklist entityID:(NSString*)entityID andDelegate:(id<STViewDelegate>)delegate;

- (id)initWithStampedBy:(id<STStampedBy>)stampedBy
              blacklist:(NSSet*)blacklist 
               entityID:(NSString*)entityID 
         includeFriends:(BOOL)includeFriends 
            andDelegate:(id<STViewDelegate>)delegate;

@end
