//
//  STStampDetailCommentsView.h
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewContainer.h"
#import "STStamp.h"

@interface STStampDetailCommentsView : UIView

- (id)initWithStamp:(id<STStamp>)stamp
        andDelegate:(id<STViewDelegate>)delegate;

@property (nonatomic, readwrite, assign) id<STViewDelegate> delegate;

@end
