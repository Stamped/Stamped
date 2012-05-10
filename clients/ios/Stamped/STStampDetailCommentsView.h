//
//  STStampDetailCommentsView.h
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewContainer.h"
#import "STStamp.h"

typedef enum {
  STStampDetailCommentsViewStyleNormal,
  STStampDetailCommentsViewStyleBlurbOnly,
} STStampDetailCommentsViewStyle;

@interface STStampDetailCommentsView : UIView

- (id)initWithStamp:(id<STStamp>)stamp 
              index:(NSInteger)index 
              style:(STStampDetailCommentsViewStyle)style 
        andDelegate:(id<STViewDelegate>)delegate;

@property (nonatomic, readwrite, assign) id<STViewDelegate> delegate;

@end
