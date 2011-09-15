//
//  LearnMoreView.h
//  Stamped
//
//  Created by Jake Zien on 9/14/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import <UIKit/UIKit.h>

@class LearnMoreChoreographer;

@interface LearnMoreView : UIView {
  LearnMoreChoreographer* choreographer;
}

@property (nonatomic, retain) IBOutlet UIScrollView*  scrollView;
@property (nonatomic, retain) LearnMoreChoreographer* choreographer;

@end
