//
//  BookDetailViewController.m
//  Stamped
//
//  Created by Jake Zien on 9/11/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "BookDetailViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "DetailedEntity.h"
#import "Entity.h"

@interface BookDetailViewController ()
- (void)setupMainActionsContainer;
- (void)setupSectionViews;
@end

@implementation BookDetailViewController

@synthesize imageView = imageView_;
@synthesize affiliateLogoView = affiliateLogoView_;

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

- (void)dealloc {
  self.imageView = nil;
  self.affiliateLogoView = nil;
  self.mainContentView = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)showContents {
  if (!detailedEntity_.author) {
    self.descriptionLabel.text = @"book";
  } else {
    self.descriptionLabel.text = [NSString stringWithFormat:@"by %@", detailedEntity_.author];
  }

  if (detailedEntity_.image) {
    self.imageView.hidden = NO;
    self.imageView.image = [UIImage imageWithData:[NSData dataWithContentsOfURL:
                                                   [NSURL URLWithString:detailedEntity_.image]]];
  }

  [self setupMainActionsContainer];
  [self setupSectionViews];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  self.scrollView.contentSize = CGSizeMake(self.view.bounds.size.width, 480);
  self.mainActionButton.hidden = YES;
  self.mainActionLabel.hidden = YES;
  self.mainActionsView.hidden = YES;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.imageView = nil;
  self.affiliateLogoView = nil;
  self.mainContentView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  self.affiliateLogoView.image = [UIImage imageNamed:@"logo_amazon"];
  
  self.imageView.layer.shadowOffset = CGSizeMake(0.0, 4.0);
  self.imageView.layer.shadowRadius = 4.0;
  self.imageView.layer.shadowColor = [UIColor blackColor].CGColor;
  self.imageView.layer.shadowOpacity = 0.33;
  self.imageView.frame = CGRectMake(self.imageView.frame.origin.x, self.imageView.frame.origin.y,
                                    self.imageView.frame.size.width, 144.0);
  self.imageView.contentMode = UIViewContentModeScaleAspectFit;
  
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (IBAction)mainActionButtonPressed:(id)sender {
  [[UIApplication sharedApplication] openURL:[NSURL URLWithString:detailedEntity_.amazonURL]];
}

#pragma mark - Content Setup (data retrieval & logic to fill views)

- (void)setupMainActionsContainer {
  if (!detailedEntity_.amazonURL) {
    self.mainActionButton.hidden = NO;
    self.mainActionLabel.hidden = NO;
    self.mainActionsView.hidden = NO;
  }
  else self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0, -CGRectGetHeight(self.mainActionsView.frame));
}


- (void) setupSectionViews {
  // Amazon Review
  if (detailedEntity_.desc) {
        
    [self addSectionWithName:@"Amazon Review" previewHeight:118.f];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Amazon Review"];
    section.collapsedFooterText = [NSString stringWithFormat:@"read more"];
    section.expandedFooterText = @"read less";
    section.footerLabel.text = section.collapsedFooterText;
    section.imageView = self.imageView;
    [section addWrappingText:detailedEntity_.desc forKey:@"desc"];
    section.arrowView.frame = CGRectOffset(section.arrowView.frame, 
                                           [section.footerLabel.text sizeWithFont:section.footerLabel.font].width + 8.0, 0);
    
    self.mainContentView.hidden = NO;
  }

  // Details
  if (detailedEntity_.format || detailedEntity_.length || detailedEntity_.language || detailedEntity_.releaseDate ||
      detailedEntity_.publisher || detailedEntity_.isbn) {
    
    [self addSectionWithName:@"Details"];
    CollapsibleViewController* section = [sectionsDict_ objectForKey:@"Details"];
    
    if (detailedEntity_.format && (detailedEntity_.length && detailedEntity_.length.intValue > 0))
      [section addPairedLabelWithName:@"Format:" 
                                value:[NSString stringWithFormat:@"%@, %@ pages", detailedEntity_.format, detailedEntity_.length] 
                               forKey:@"format"];
    else if (detailedEntity_.format)
      [section addPairedLabelWithName:@"Format:" 
                                value:detailedEntity_.format 
                               forKey:@"format"];
    else if (detailedEntity_.length && (detailedEntity_.length && detailedEntity_.length.intValue > 0))
      [section addPairedLabelWithName:@"Length:" 
                                value:[NSString stringWithFormat:@"%@ pages", detailedEntity_.length] 
                               forKey:@"length"];
    if (detailedEntity_.publisher)
      [section addPairedLabelWithName:@"Publisher:" 
                                value:detailedEntity_.publisher
                               forKey:@"publisher"];
    if (detailedEntity_.releaseDate)
      [section addPairedLabelWithName:@"Release Date:" 
                                value:detailedEntity_.releaseDate 
                               forKey:@"releaseDate"];
    if (detailedEntity_.language)
      [section addPairedLabelWithName:@"Language:" 
                                value:detailedEntity_.language 
                               forKey:@"language"];
    if (detailedEntity_.isbn)
      [section addPairedLabelWithName:@"ISBN:" 
                                value:detailedEntity_.isbn 
                               forKey:@"isbn"];
    
    self.mainContentView.hidden = NO;
  }

  // Stamped by.
  NSSet* stamps = entityObject_.stamps;

  if (stamps && stamps.count > 0) {
    [self addSectionStampedBy];
    self.mainContentView.hidden = NO; 
  }
}

@end
