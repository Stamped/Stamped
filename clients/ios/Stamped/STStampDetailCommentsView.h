//
//  STStampDetailCommentsView.h
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewContainer.h"
#import "STStamp.h"

@interface STStampDetailCommentsView : STViewContainer

- (id)initWithStamp:(id<STStamp>)stamp index:(NSInteger)index andDelegate:(id<STViewDelegate>)delegate;

@property (nonatomic, readonly, retain) UITextField* addCommentView;

@end
