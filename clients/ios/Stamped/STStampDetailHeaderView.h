//
//  STStampDetailHeaderView.h
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStamp.h"
#import "STEntity.h"
#import "STViewContainer.h"

@interface STStampDetailHeaderView : STViewContainer

-(id)initWithStamp:(id<STStamp>)stamp;

@end
