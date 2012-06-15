//
//  PostStampGraphView.m
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import "PostStampGraphView.h"
#import "STStampContainerView.h"

@implementation PostStampGraphView

- (id)initWithFrame:(CGRect)frame {

    if ((self = [super initWithFrame:frame])) {

        STStampContainerView *view = [[STStampContainerView alloc] initWithFrame:self.bounds];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [self addSubview:view];
        [view release];
        
    }
    return self;
}


@end
